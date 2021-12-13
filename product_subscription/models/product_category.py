# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Carmen Bianca Bakker <carmen@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api


class ProductCategory(models.Model):
    _name = "product.template.category"
    _description = "Product Category"

    name = fields.Char(string="Name", copy=False, required=True)
