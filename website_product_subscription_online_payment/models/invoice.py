# -*- coding: utf-8 -*-
from openerp import models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def post_process_confirm_sub_paid(self, effective_date):
        request = self.product_subscription_request
        if (request.payment_type == 'deferred'
                and not request.subscription_template.split_payment):
            self.process_subscription(effective_date)

        return True
