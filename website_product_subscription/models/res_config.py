# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api

PARAMS = [
    ('product_subscription_form_header',
     'website_product_subscription.product_subscription_form_header'),
]


class WebsiteConfigSettings(models.Model):
    _inherit = 'website.config.settings'

    @api.multi
    def set_params(self):
        self.ensure_one()

        for field_name, key_name in PARAMS:
            value = getattr(self, field_name)
            self.env['ir.config_parameter'].set_param(key_name, str(value))

    product_subscription_form_header = fields.Html(
        string='Product Subscription Form Header Text',
        translate=True,
        required=False)
