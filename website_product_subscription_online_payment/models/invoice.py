# -*- coding: utf-8 -*-
from openerp import models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def post_process_confirm_sub_paid(self, effective_date):
        # payment type is false when chosen type is deferred because no
        # payment transaction is created in that case.
        # quick fix was to use the not condition,
        # todo a better fix would be to create a transaction in each case
        if (not self.product_subscription_request.payment_type
            or (self.product_subscription_request.payment_type == 'deferred'
                and not self.subscription_template.split_payment)):
            self.process_subscription(effective_date)

        return True
