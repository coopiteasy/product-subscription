# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRLfs <http://coopiteasy.be>
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.http import request
from openerp.addons.website_product_subscription.controllers.subscribe import (
    SubscribeController,
)


class SubscribeWebAccess(SubscribeController):
    def get_subscription_request_values(self):
        vals = super(
            SubscribeWebAccess, self
        ).get_subscription_request_values()
        params = request.params
        if params["is_gift"]:
            vals["websubscriber"] = params["subscriber_id"]
        else:
            vals["websubscriber"] = params["sponsor_id"]
        return vals
