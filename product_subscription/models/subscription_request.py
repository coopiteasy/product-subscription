# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api, _
from openerp.exceptions import UserError


class SubscriptionRequest(models.Model):
    _name = "product.subscription.request"
    _description = "Subscription Request"
    _order = "subscription_date desc, id desc"

    name = fields.Char(string="Name", copy=False)
    # deprecated
    gift = fields.Boolean(string="Gift?")
    type = fields.Selection(
        string="Type",
        selection=[("basic", "Basic"), ("gift", "Gift")],
        default="basic",
        required=True,
    )
    is_company = fields.Boolean(string="Company?")
    # todo rename invoicee_id
    sponsor = fields.Many2one(
        comodel_name="res.partner",
        string="Sponsor",
        help="The sponsor is the partner paying the subscription",
        required=True,
    )
    subscriber = fields.Many2one(
        comodel_name="res.partner",
        string="Subscriber",
        help="The subscriber is the partner receiving the subscription",
        required=True,
    )
    subscription_date = fields.Date(
        string="Subscription request date", default=fields.Date.today()
    )
    payment_date = fields.Date(
        string="Payment date",
        readonly=True,
        copy=False
    )
    invoice = fields.Many2one(
        comodel_name="account.invoice",
        string="Invoice",
        readonly=True,
        copy=False
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("sent", "Sent"),
            ("paid", "Paid"),
            ("cancel", "Cancelled"),
        ],
        string="State",
        default="draft",
    )
    subscription = fields.Many2one(
        comodel_name="product.subscription.object",
        string="Subscription",
        readonly=True,
        copy=False,
    )
    subscription_template = fields.Many2one(
        comodel_name="product.subscription.template",
        string="Subscription template",
        required=True,
    )

    def _get_account(self, partner, product):
        account = (
            product.property_account_income_id
            or product.categ_id.property_account_income_categ_id
        )
        if not account:
            raise UserError(
                _(
                    "Please define income account for this"
                    ' product: "%s" (id:%d) - or for its'
                    ' category: "%s".'
                )
                % (product.name, product.id, product.categ_id.name)
            )

        fpos = partner.property_account_position_id
        if fpos:
            account = fpos.map_account(account)
        return account

    def _prepare_invoice_line(self, product, partner, qty):
        self.ensure_one()

        account = self._get_account(partner, product)

        res = {
            "name": product.name,
            "account_id": account.id,
            "price_unit": product.lst_price,
            "quantity": qty,
            "uom_id": product.uom_id.id,
            "product_id": product.id or False,
            "invoice_line_tax_ids": [(6, 0, product.taxes_id.ids)],
        }
        return res

    def send_invoice(self, invoice):
        invoice_email_template = self.env.ref(
            "account.email_template_edi_invoice", False
        )

        # we send the email with invoice in attachment
        invoice_email_template.send_mail(invoice.id)  # todo slow
        invoice.sent = True

    @api.multi
    def create_invoice(self, partner, vals={}):
        self.ensure_one()
        # creating invoice and invoice lines
        vals.update(
            {
                "partner_id": partner.id,
                "subscription": True,
                "journal_id": self.subscription_template.journal.id,
                "type": "out_invoice",
            }
        )

        invoice = self.env["account.invoice"].create(vals)

        # does not support product variant
        product = self.subscription_template.product.product_variant_ids[0]
        vals = self._prepare_invoice_line(product, partner, 1)
        vals["invoice_id"] = invoice.id

        if self.subscription_template.analytic_distribution:
            vals[
                "analytic_distribution_id"
            ] = self.subscription_template.analytic_distribution.id

        self.env["account.invoice.line"].create(vals)
        invoice.compute_taxes()
        self.invoice = invoice
        return invoice

    @api.model
    def create(self, vals):
        prod_sub_req_seq = self.env.ref(
            "product_subscription.sequence_product_subscription_request", False
        )

        prod_sub_num = prod_sub_req_seq.next_by_id()
        vals["name"] = prod_sub_num

        return super(SubscriptionRequest, self).create(vals)

    @api.multi
    def validate_request(self):
        for request in self:
            partner = request.sponsor
            invoice = request.create_invoice(partner, {})
            invoice.signal_workflow("invoice_open")
            request.send_invoice(invoice)
            request.state = "sent"

    @api.multi
    def force_subscription(self):
        self.ensure_one()
        if self.subscription_template.split_payment:
            if not self.subscription:
                now = fields.Datetime.now()
                self.invoice.process_subscription(now)
            else:
                raise UserError(
                    _(
                        "A subscription already exists for this "
                        " subscription request"
                    )
                )
        else:
            raise UserError(
                _(
                    "Forcing a subscription is only possible for"
                    " subscription request with partial payment"
                )
            )
        return True

    @api.multi
    def cancel_request(self):
        for request in self:
            request.state = "cancel"

    @api.multi
    def action_draft(self):
        for request in self:
            request.state = "draft"

    @api.model
    def _validate_pending_request(self):
        pending_request_list = self.search([("state", "=", "draft")])

        # we loop to avoid a whole roll back in case of
        # one of the request validation fails
        for pending_request in pending_request_list:
            try:
                pending_request.validate_request()
            except UserError:
                # todo: notify
                continue

    @api.model
    def _migrate_gift_to_type(self):
        requests = self.search([("gift", "=", True)])
        subscriptions = requests.mapped("subscription")
        requests.write({"type": "gift"})
        subscriptions.write({"type": "gift"})
