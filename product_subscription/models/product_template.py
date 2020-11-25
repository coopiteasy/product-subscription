# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    subscription = fields.Boolean(string="Subscription")
    product_qty = fields.Integer(  # todo duplicate field?
        string="Product quantity"
    )
