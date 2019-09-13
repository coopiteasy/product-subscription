# -*- coding: utf-8 -*-
from openerp import fields, models


class ProductSubscriptionRequest(models.Model):
    _inherit = 'product.subscription.request'

    payment_transaction = fields.One2many('payment.transaction',
                                          'product_subscription_request_id')
    transaction_state = fields.Selection(related='payment_transaction.state',
                                         string="Transaction status")
    payment_type = fields.Selection(related='payment_transaction.payment_type',
                                    string='Payment Type')

    def send_invoice(self, invoice):
        if (self.payment_type == 'deferred'
                or self.subscription_template.split_payment):
            super(ProductSubscriptionRequest, self).send_invoice(invoice)
