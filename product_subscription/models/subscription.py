# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    firstname = fields.Char(  # fixme how does it interact with module partner_firstname?
        string='First Name')
    lastname = fields.Char(
        string='Last Name')
    subscriber = fields.Boolean(
        string='Subscriber',
        compute='_compute_is_subscriber')
    old_subscriber = fields.Boolean(
        string='Old subscriber',
        compute='_compute_is_subscriber')
    subscriptions = fields.One2many(
        comodel_name='product.subscription.object',
        inverse_name='subscriber',
        string='Subscription')

    @api.multi
    def _compute_is_subscriber(self):
        for partner in self:
            subscriptions = partner.subscriptions.filtered(
                lambda s: s.state not in 'draft'
            )
            active = partner.subscriptions.filtered(
                lambda s: s.state in ['ongoing', 'renew']
            )
            if subscriptions and active:
                partner.subscriber = True
                partner.old_subscriber = False
            elif subscriptions and not active:
                partner.subscriber = False
                partner.old_subscriber = True
            else:
                # never subscribed
                partner.subscriber = False
                partner.old_subscriber = False


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    subscription = fields.Boolean(
        string='Subscription')
    product_qty = fields.Integer(  # todo duplicate field?
        string='Product quantity')
    subscription_templates = fields.Many2many(
        comodel_name='product.subscription.template',
        string='Subscription Templates')


class SubscriptionTemplate(models.Model):
    _name = 'product.subscription.template'

    name = fields.Char(
        string='Subscription name',
        copy=False,
        required=True)
    description = fields.Char(
        string='Description')
    product_qty = fields.Integer(  # todo duplicate field?
        string='Subscription quantity',
        required=True,
        help='This is the quantity of product that'
             ' will be allocated by this subscription')
    price = fields.Float(
        related='product.lst_price',
        string='Subscription price',
        readonly=True)
    publish = fields.Boolean(
        string='Publish on website')
    product = fields.Many2one(
        comodel_name='product.template',
        string='Product',
        domain=[('subscription', '=', True)],
        required=True)
    released_products = fields.Many2many(
        comodel_name='product.template',
        string='Released Product')
    analytic_distribution = fields.Many2one(
        comodel_name='account.analytic.distribution',
        string='Analytic distribution')
    journal = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        required=True,
        domain=[('type', '=', 'sale')])


class SubscriptionRequest(models.Model):
    _name = 'product.subscription.request'
    _order = 'subscription_date desc, id desc'

    name = fields.Char(
        string='Name',
        copy=False)
    gift = fields.Boolean(
        string='Gift?')
    is_company = fields.Boolean(
        string='Company?')
    sponsor = fields.Many2one(
        comodel_name='res.partner',
        string='Sponsor')
    subscriber = fields.Many2one(
        comodel_name='res.partner',
        string='Subscriber',
        required=True)
    subscription_date = fields.Date(
        string='Subscription request date',
        default=fields.Date.today())
    payment_date = fields.Date(
        string='Payment date',
        readonly=True)
    invoice = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice',
        readonly=True,
        copy=False)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('sent', 'Sent'),
         ('paid', 'Paid'),
         ('cancel', 'Cancelled')],
        string='State',
        default='draft')
    subscription = fields.Many2one(
        comodel_name='product.subscription.object',
        string='Subscription',
        readonly=True,
        copy=False)
    subscription_template = fields.Many2one(
        comodel_name='product.subscription.template',
        string='Subscription template',
        required=True)

    def _get_account(self, partner, product):
        account = (product.property_account_income_id or
                   product.categ_id.property_account_income_categ_id)
        if not account:
            raise UserError(_('Please define income account for this'
                              ' product: "%s" (id:%d) - or for its'
                              ' category: "%s".') %
                            (product.name, product.id, product.categ_id.name))

        fpos = partner.property_account_position_id
        if fpos:
            account = fpos.map_account(account)
        return account

    def _prepare_invoice_line(self, product, partner, qty):
        self.ensure_one()

        account = self._get_account(partner, product)

        res = {
            'name': product.name,
            'account_id': account.id,
            'price_unit': product.lst_price,
            'quantity': qty,
            'uom_id': product.uom_id.id,
            'product_id': product.id or False,
            'invoice_line_tax_ids': [(6, 0, product.taxes_id.ids)]
        }
        return res

    def send_invoice(self, invoice):
        invoice_email_template = self.env.ref('account.email_template_edi_invoice', False)

        # we send the email with invoice in attachment
        invoice_email_template.send_mail(invoice.id)  # todo slow
        invoice.sent = True

    def create_invoice(self, partner, vals={}):
        # creating invoice and invoice lines
        vals.update({'partner_id': partner.id,
                     'subscription': True,
                     'journal_id': self.subscription_template.journal.id,
                     'type': 'out_invoice'})

        invoice = self.env['account.invoice'].create(vals)

        # does not support product variant
        pproduct = self.subscription_template.product.product_variant_ids[0]
        vals = self._prepare_invoice_line(pproduct, partner, 1)
        vals['invoice_id'] = invoice.id

        if self.subscription_template.analytic_distribution:
            vals['analytic_distribution_id'] = self.subscription_template.analytic_distribution.id

        self.env['account.invoice.line'].create(vals)

        return invoice

    @api.model
    def create(self, vals):
        prod_sub_req_seq = self.env.ref(
            'product_subscription.sequence_product_subscription_request',
            False)

        prod_sub_num = prod_sub_req_seq.next_by_id()
        vals['name'] = prod_sub_num

        return super(SubscriptionRequest, self).create(vals)

    @api.multi
    def validate_request(self):
        for request in self:
            partner = request.subscriber
            # if it's a gift then the sponsor is set on the invoice
            if request.gift:
                partner = request.sponsor

            invoice = request.create_invoice(partner, {})
            invoice.compute_taxes()
            invoice.signal_workflow('invoice_open')
            request.send_invoice(invoice)
            request.write({'state': 'sent', 'invoice': invoice.id})

    @api.multi
    def cancel_request(self):
        for request in self:
            request.state = 'cancel'

    @api.multi
    def action_draft(self):
        for request in self:
            request.state = 'draft'

    @api.model
    def _validate_pending_request(self):
        pending_request_list = self.search([('state', '=', 'draft')])

        for pending_request in pending_request_list:
            try:
                pending_request.validate_request()
            except UserError:
                # todo: notify
                continue


class SubscriptionObject(models.Model):
    _name = 'product.subscription.object'
    _order = 'subscribed_on desc'

    name = fields.Char(
        string='Name',
        copy=False,
        required=True)
    subscriber = fields.Many2one(
        comodel_name='res.partner',
        string='Subscriber',
        required=True)
    counter = fields.Float(
        string='Counter')
    subscribed_on = fields.Date(
        string='First subscription date')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('ongoing', 'Ongoing'),
         ('renew', 'Need to Renew'),
         ('terminated', 'Terminated')],
        string='State',
        default='draft')
    request = fields.Many2one(
        comodel_name='product.subscription.request',
        string='Subscription Request')
    template = fields.Many2one(
        comodel_name='product.subscription.template',
        required=True)

    @api.model
    def create(self, vals):
        subscription_sequence = (
            self.env.ref('product_subscription.sequence_product_subscription',
                         False)
         )
        prod_sub_num = subscription_sequence.next_by_id()
        vals['name'] = prod_sub_num
        vals['state'] = 'draft'

        return super(SubscriptionObject, self).create(vals)

    # todo use write for batch processing
    # @api.multi
    # @api.depends('counter')
    # def _compute_state(self):
    #     for subscription in self:
    #         if not subscription.counter:
    #             subscription.state = 'draft'
    #         elif subscription.counter == 0:
    #             subscription.state = 'terminated'
    #         elif subscription.counter == 1:
    #             subscription.state = 'renew'
    #         else:
    #             subscription.state = 'ongoing'
