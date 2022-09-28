# -*- coding: utf-8 -*-
from openerp import api, models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    @api.model
    def _mollie_form_validate(self, tx, data):
        result = super(PaymentTransaction, self)._mollie_form_validate(tx, data)
        if result:
            self.process_prod_sub_online_payment_reception(tx)
        return result
