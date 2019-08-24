# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ProductSubscriptionTemplate(models.Model):
    _inherit = 'product.subscription.template'

    is_web_subscription = fields.Boolean(
        string='Web Subscription',
        required=False)


class ProductSubscriptionObject(models.Model):
    _inherit = 'product.subscription.object'

    is_web_subscription = fields.Boolean(
        related='template.is_web_subscription')
