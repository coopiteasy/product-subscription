# -*- coding: utf-8 -*-
from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

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
