# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ProductSubscriptionTemplate(models.Model):
    _inherit = "product.subscription.template"

    is_web_subscription = fields.Boolean(
        string="Web Subscription", required=False
    )

    web_access_presentation = fields.Html(
        string="Web Access Explanation Text",
        help="Text displayed on the website forms",
    )


class ProductSubscriptionObject(models.Model):
    _inherit = "product.subscription.object"

    is_web_subscription = fields.Boolean(
        related="template.is_web_subscription"
    )


class ProductSubscriptionRequest(models.Model):
    _inherit = "product.subscription.request"

    is_web_subscription = fields.Boolean(
        related="subscription_template.is_web_subscription"
    )
    websubscriber = fields.Many2one(
        comodel_name="res.partner",
        string="Web Subscriber",
        help=(
            "The websubscriber is the partner recieving the web access "
            "medor online."
        ),
        required=True,
    )
