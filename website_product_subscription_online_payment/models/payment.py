# -*- coding: utf-8 -*-
from datetime import datetime
import logging

from openerp import api, fields, models

_logger = logging.getLogger(__name__)


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    payment_type = fields.Selection([('online', 'Online'),
                                     ('deferred', 'Deferred')],
                                    string='Payment Type',
                                    default="deferred")


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    payment_type = fields.Selection(related='acquirer_id.payment_type',
                                    readonly=True)
    product_subscription_request_id = fields.Many2one(
                                      'product.subscription.request',
                                      string="Product subscription"
                                      " request",
                                      readonly=True)

    @api.model
    def process_prod_sub_online_payment_reception(self, tx):
        if tx.product_subscription_request_id:
            prod_sub_request = tx.product_subscription_request_id
            prod_sub_request.state = 'paid'
            now = datetime.now().strftime("%d/%m/%Y")
            prod_sub_request.sudo().invoice.process_subscription(now)

        return True
