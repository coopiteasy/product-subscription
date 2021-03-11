# -*- coding: utf-8 -*-
from datetime import datetime
import logging

from openerp import api, fields, models

_logger = logging.getLogger(__name__)


class PaymentAcquirer(models.Model):
    _inherit = "payment.acquirer"

    payment_type = fields.Selection(
        [("online", "Online"), ("deferred", "Deferred")],
        string="Payment Type",
        default="deferred",
    )


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"
    payment_type = fields.Selection(
        related="acquirer_id.payment_type", readonly=True
    )
    product_subscription_request_id = fields.Many2one(
        "product.subscription.request",
        string="Product subscription" " request",
        readonly=True,
    )

    show_button = fields.Boolean(
        string="Show button",
        help="computed field to show button allowing to create "
        "missing subscription",
        compute="_show_button_create")

    @api.multi
    def _show_button_create(self):
        for tx in self:
            if (
                tx.payment_type == "online"
                and tx.state == "done"
                and tx.product_subscription_request_id
                and len(tx.product_subscription_request_id.subscription) == 0
            ):
                tx.show_button = True

    @api.model
    def process_prod_sub_online_payment_reception(self, tx):
        if (tx.product_subscription_request_id and
                len(self.product_subscription_request_id.subscription) == 0):
            prod_sub_request = tx.product_subscription_request_id
            prod_sub_request.state = "paid"
            now = datetime.now().strftime("%d/%m/%Y")
            prod_sub_request.sudo().invoice.process_subscription(now)

        return True

    @api.multi
    def create_subscription(self):
        self.ensure_one()
        self.process_prod_sub_online_payment_reception(self)
