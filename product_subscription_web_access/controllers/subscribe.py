# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRLfs <http://coopiteasy.be>
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import http
from openerp.exceptions import ValidationError
from openerp.http import request
from openerp.tools.translate import _

from openerp.addons.website_product_subscription.controllers.subscribe import SubscribeController


class SubscribeWebAccess(SubscribeController):

    def get_subscription_request_values(self, params, gift):
        vals = super(
            SubscribeWebAccess, self
        ).get_subscription_request_values(params, gift)
        if gift:
            vals['websubscriber'] = params['subscriber_id']
        else:
            vals['websubscriber'] = params['sponsor_id']
        return vals
