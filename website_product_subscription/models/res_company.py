# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"

    company_condition_text = fields.Html(
        string="Company Condition Text", translate=True, required=False
    )
