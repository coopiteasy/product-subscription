# -*- coding: utf-8 -*-
from openerp import fields, models


class ProductSubscriptionRequest(models.Model):
    _inherit = 'product.subscription.request'

    payment_transaction = fields.One2many('payment.transaction',
                                          'product_subscription_request_id')
    payment_type = fields.Selection(related='payment_transaction.payment_type',
                                    string='Payment Type')

    def send_invoice(self, invoice):
        if self.payment_type == 'deferred':
            super(ProductSubscriptionRequest, self).send_invoice(invoice)
