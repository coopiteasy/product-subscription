# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ProductSubscriptionTemplateForms(models.Model):
    _name = "product.subscription.template.form"

    name = fields.Char()


class ProductSubscriptionTemplate(models.Model):
    _inherit = "product.subscription.template"

    presentation_text = fields.Html(
        string="Subscription Presentation Text",
        help="Text displayed on the website forms",
    )
    allowed_form_ids = fields.Many2many(
        comodel_name="product.subscription.template.form",
        string="Allowed Forms",
        relation="product_subscription_template_form_rel",
    )
