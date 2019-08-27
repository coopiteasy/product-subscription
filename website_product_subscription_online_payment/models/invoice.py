# -*- coding: utf-8 -*-
from openerp import models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def post_process_confirm_paid(self, effective_date):
        if self.product_subscription_request.payment_type == 'deferred':
            self.process_subscription(effective_date)

        return True
