# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import fields, models, api


class ProductSubscriptionRequest(models.Model):
    _inherit = "product.subscription.request"

    origin = fields.Selection(
        [("website", "Website"), ("manual", "Manual")],
        string="Source",
        default="manual",
        readonly=True,
    )
    payment_transaction = fields.One2many(
        comodel_name="payment.transaction",
        inverse_name="product_subscription_request_id",
    )
    transaction_state = fields.Selection(
        related="payment_transaction.state",
        string="Transaction status",
        readonly=True
    )
    payment_type = fields.Selection(
        related="payment_transaction.payment_type",
        string="Payment Type",
        store=True
    )

    def send_invoice(self, invoice):
        if (
            self.payment_type == "deferred"
            or self.subscription_template.split_payment
        ):
            super(ProductSubscriptionRequest, self).send_invoice(invoice)

    @api.multi
    def validate_request(self):
        super(ProductSubscriptionRequest, self).validate_request()
        for request in self:
            if request.origin == "manual" and not request.payment_transaction:
                acquirer = self.env.ref(
                    "payment_transfer.payment_acquirer_transfer"
                )
                self.env["payment.transaction"].create(
                    {
                        "reference": request.invoice.number,
                        "amount": request.invoice.residual,
                        "currency_id": request.invoice.currency_id.id,
                        "acquirer_id": acquirer.id,
                        "product_subscription_request_id": request.id,
                    }
                )
            # Without knowing why sometime the related field is not set.
            # For such case we make an explicit assignment.
            if not request.payment_type:
                request.payment_type = request.payment_transaction.payment_type
