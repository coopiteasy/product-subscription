# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

from openerp.exceptions import UserError


class SubscriptionRequest(models.Model):
    _inherit = "product.subscription.request"

    def get_available_carriers(self, partner_id):
        carriers = self.env["delivery.carrier"].search(
            [("shipping_enabled", "=", True)]
        )
        available_carriers = []
        for carrier in carriers:
            if carrier.verify_carrier(partner_id):
                available_carriers.append(carrier)

        return available_carriers

    carrier_id = fields.Many2one(
        "delivery.carrier",
        domain=[("shipping_enabled", "=", True)],
        string="Delivery Method",
    )

    @api.onchange("carrier_id")
    def onchange_carrier(self):
        if self.carrier_id:
            if not self.carrier_id.verify_carrier(self.subscriber):
                raise UserError(
                    _(
                        "This carrier is not available for this"
                        "subscriber. Please select another one"
                    )
                )
            else:
                available_carriers = self.get_available_carriers(
                    self.subscriber
                )
                if available_carriers:
                    self.carrier_id = available_carriers[0]

    def create_invoice(self, partner, vals=None):
        if vals is None:
            vals = {}

        if self.carrier_id:
            carrier = self.carrier_id
        else:
            available_carriers = self.get_available_carriers(self.subscriber)
            if available_carriers:
                self.carrier_id = available_carriers[0]
                carrier = self.carrier_id

        if not carrier:
            raise UserError(_("No carrier matching."))

        # The delivery type is based on fixed price
        carrier.verify_carrier(self.subscriber)
        delivery_product = carrier.product_id
        quantity = self.subscription_template.product_qty

        subscription_product = self.subscription_template.product.product_variant_ids[
            0
        ]
        weight = (subscription_product.weight or 0.0) * quantity
        volume = (subscription_product.volume or 0.0) * quantity
        price_unit = carrier.get_price_from_picking(
            subscription_product.list_price, weight, volume, quantity
        )

        # todo do we need to convert price_unit using currency?

        delivery_line = self._prepare_invoice_line(
            delivery_product,
            self.subscriber,
            quantity=quantity,
            price_unit=price_unit,
            is_delivery=True,
        )

        if "invoice_line_ids" in vals:
            vals["invoice_line_ids"].append((0, 0, delivery_line))
        else:
            vals["invoice_line_ids"] = [(0, 0, delivery_line)]

        vals["carrier_id"] = carrier.id
        vals["address_shipping_id"] = self.subscriber.id

        invoice = super(SubscriptionRequest, self).create_invoice(
            partner, vals
        )
        return invoice
