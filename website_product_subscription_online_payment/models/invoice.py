# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import models, api, _
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def confirm_paid(self):
        for invoice in self:
            sub_request = invoice.product_subscription_request
            refund = self.search(
                [
                    ("type", "=", "out_refund"),
                    ("origin", "=", invoice.move_name),
                ]
            )
            if (
                sub_request.payment_transaction
                or not invoice.subscription
                or refund
            ):
                super(AccountInvoice, invoice).confirm_paid()
            elif invoice.residual > 0 and not sub_request.payment_transaction:
                raise ValidationError(
                    _(
                        "Can't confirm the payment. There is "
                        "no transaction associated to the "
                        "subscription request "
                    )
                )

    def post_process_confirm_sub_paid(self, effective_date):
        request = self.product_subscription_request
        if (
            request.payment_type == "deferred"
            and not request.subscription_template.split_payment
        ):
            self.process_subscription(effective_date)

        return True

    @api.multi
    def send_confirm_paid_email(self):
        """Send an email to confirm the payment of this invoice."""
        conf_email_template = self.env.ref(
            "product_subscription"
            ".subscription_payment_confirmation_email_template"
        )
        for invoice in self:
            request = invoice.product_subscription_request
            if not request.subscription_template.split_payment:
                conf_email_template.send_mail(invoice.id)
