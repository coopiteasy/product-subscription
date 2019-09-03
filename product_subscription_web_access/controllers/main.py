# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.addons.website_product_subscription.controllers.main import WebsiteProductSubscription
from openerp.http import request


class WebsiteProductSubscription(WebsiteProductSubscription):

    def fill_values(self, values, load_from_user=False):
        values = super(WebsiteProductSubscription, self).fill_values(values, load_from_user=False)

        product_subscription_web_access = request.env['ir.config_parameter'].get_param('product_subscription_web_access.product_subscription_web_access')
        values['product_subscription_web_access'] = product_subscription_web_access or ''
        return values
