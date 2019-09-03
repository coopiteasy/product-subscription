# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api

PARAMS = [
    ('product_subscription_web_access',
     'product_subscription_web_access.product_subscription_web_access'),
]


class WebsiteConfigSettings(models.Model):
    _inherit = 'website.config.settings'

    @api.multi
    def set_params(self):
        self.ensure_one()
        res = super(WebsiteConfigSettings, self).set_params()
        for field_name, key_name in PARAMS:
            value = getattr(self, field_name)
            self.env['ir.config_parameter'].set_param(key_name, str(value))
        return res

    product_subscription_web_access = fields.Html(
        string='Product Subscription Web Access Text',
        translate=True,
        required=False)
