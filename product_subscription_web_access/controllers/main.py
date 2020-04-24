# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.addons.website_product_subscription.controllers.subscribe import (
    SubscribeController
)
from openerp import http
from openerp.http import request


class WebsiteProductSubscription(SubscribeController):
    @http.route(
        ["/subscription/field/web_access_presentation"],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def get_subscription_web_access_presentation(
        self, sub_template_id=None, **kw
    ):
        if sub_template_id is None:
            return {}
        else:
            sub_temp_obj = request.env["product.subscription.template"]
            subs_temp = sub_temp_obj.sudo().browse(int(sub_template_id))
            return {
                subs_temp.id: {
                    "web_access_presentation": subs_temp.web_access_presentation
                }
            }

    def create_subscription_request(self, **kw):
        vals = {
            "subscriber": kw.get("subscriber_id"),
            "websubscriber": kw.get("subscriber_id"),
            "subscription_template": int(kw.get("product_subscription_id")),
            "gift": kw.get("gift") == "on",
            "sponsor": kw.get("sponsor_id"),
        }
        sub_request = (
            request.env["product.subscription.request"].sudo().create(vals)
        )
        return sub_request
