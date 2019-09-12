# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ProductSubscriptionTemplate(models.Model):
    _inherit = 'product.subscription.template'

    presentation_text = fields.Html(
        string='Subscription Presentation Text',
        help='Text displayed on the website forms')
