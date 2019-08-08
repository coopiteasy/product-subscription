# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    subscription = fields.Boolean(
        string='Subscription')
    product_subscription_request = fields.One2many(
                'product.subscription.request',
                'invoice',
                string='Product subscription')

    @api.multi
    def process_subscription(self, effective_date):
        self.ensure_one()

        subscription_template = (
            self.product_subscription_request.subscription_template
        )
        subscriber = self.product_subscription_request.subscriber
        subscription_sequence = (
            self.env.ref('product_subscription.sequence_product_subscription',
                         False)
         )

        subscription = self.env['product.subscription.object'].create({
            'name': subscription_sequence.next_by_id(),
            'subscriber': subscriber.id,
            'subscribed_on': effective_date,
            'counter': subscription_template.product_qty,
            'state': 'ongoing',
            'subscription_template': subscription_template.id,
        })

        subscriber.write({
            'subscriber': True,
            'old_subscriber': False,
        })

        self.product_subscription_request.write({
            'state': 'paid',
            'payment_date': effective_date,
            'subscription': subscription.id,
        })

        self.send_confirm_paid_email()
        return True

    @api.multi
    def confirm_paid(self):
        for invoice in self:
            super(AccountInvoice, invoice).confirm_paid()
            # we check if there is an open refund for this invoice. in this
            # case we don't run the process_subscription function as the
            # invoice has been reconciled with a refund and not a payment.
            refund = self.search([('type', '=', 'out_refund'),
                                  ('origin', '=', invoice.move_name)])

            if invoice.subscription and invoice.type == 'out_invoice' and not refund:
                effective_date = datetime.now().strftime('%Y-%m-%d')
                # effective_date = datetime.now().strftime('%d/%m/%Y')  fixme was this, why?

                # take the effective date from the payment.
                # by default the confirmation date is the payment date
                if invoice.payment_move_line_ids:
                    move_line = invoice.payment_move_line_ids[0]
                    effective_date = move_line.date

                invoice.process_subscription(effective_date)
        return True

    @api.multi
    def send_confirm_paid_email(self):
        """Send an email to confirm the payment of this invoice."""
        conf_email_template = self.env.ref(
            'product_subscription'
            '.subscription_payment_confirmation_email_template'
        )
        for invoice in self:
            conf_email_template.send_mail(invoice.id)
