# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

from openerp.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    carrier_id = fields.Many2one("delivery.carrier", string="Delivery Method")
    address_shipping_id = fields.Many2one(
        "res.partner",
        string="Shipping Address",
        readonly=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
        help="Delivery address for current invoice.",
    )

    @api.multi
    def _delivery_unset(self):
        self.env["account.invoice.line"].search(
            [("invoice_id", "in", self.ids), ("is_delivery", "=", True)]
        ).unlink()


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    is_delivery = fields.Boolean(string="Is a Delivery", default=False)
