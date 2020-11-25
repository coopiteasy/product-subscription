# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DTF


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    subscription = fields.Boolean(string="Subscription")
    product_subscription_request = fields.One2many(  # only one
        comodel_name="product.subscription.request",
        inverse_name="invoice",
        string="Product subscription",
    )

    @api.multi
    def get_next_start_date(self, subscriber):
        self.ensure_one()
        subscriptions = subscriber.subscriptions.filtered(
            lambda s: s.state in ["renew", "ongoing"]
        )

        if subscriptions:
            last = subscriptions.sorted(lambda s: s.end_date, reverse=True)[0]
            if last.end_date:
                end = datetime.strptime(last.end_date, DTF)
                start_date = end + timedelta(days=1)
                return start_date.strftime(DTF)
            else:
                return False
        else:
            return False

    @api.multi
    def process_subscription(self, effective_date):
        # todo should be delegated to subscription request
        self.ensure_one()
        srequest = self.product_subscription_request

        template = srequest.subscription_template
        subscriber = srequest.subscriber
        try:
            effective_date = datetime.strptime(
                effective_date, "%d/%m/%Y"
            ).strftime(DTF)
        except ValueError:
            effective_date = effective_date

        if self.get_next_start_date(subscriber):
            start_date = self.get_next_start_date(subscriber)
        elif srequest.type == "gift" and srequest.gift_date:
            start_date = srequest.gift_date
        else:
            start_date = effective_date

        subscription = self.env["product.subscription.object"].create(
            {
                "subscriber": subscriber.id,
                "subscribed_on": effective_date,
                "start_date": start_date,
                "counter": template.product_qty,
                "state": "ongoing",
                "request": srequest.id,
                "template": template.id,
                "type": srequest.type,
            }
        )

        vals = {
            "state": "paid",
            "payment_date": effective_date,
            "subscription": subscription.id,
        }

        if template.split_payment:
            vals["state"] = "sent"

        srequest.write(vals)

        self.send_confirm_paid_email()
        return True

    def post_process_confirm_sub_paid(self, effective_date):
        self.process_subscription(effective_date)

        return True

    @api.multi
    def confirm_paid(self):
        for invoice in self:
            super(AccountInvoice, invoice).confirm_paid()
            # we check if there is an open refund for this invoice. in this
            # case we don't run the process_subscription function as the
            # invoice has been reconciled with a refund and not a payment.
            refund = self.search(
                [
                    ("type", "=", "out_refund"),
                    ("origin", "=", invoice.move_name),
                ]
            )

            if (
                invoice.subscription
                and invoice.type == "out_invoice"
                and not refund
            ):
                # seems that doing it this way strftime('%Y-%m-%d') doesn't
                # work  wtf
                effective_date = datetime.now().strftime("%d/%m/%Y")

                # take the effective date from the payment.
                # by default the confirmation date is the payment date
                if invoice.payment_move_line_ids:
                    move_line = invoice.payment_move_line_ids[0]
                    effective_date = move_line.date

                invoice.post_process_confirm_sub_paid(effective_date)
        return True

    @api.multi
    def send_confirm_paid_email(self):
        """Send an email to confirm the payment of this invoice."""
        conf_email_template = self.env.ref(
            "product_subscription"
            ".subscription_payment_confirmation_email_template"
        )
        for invoice in self:
            conf_email_template.send_mail(invoice.id)
