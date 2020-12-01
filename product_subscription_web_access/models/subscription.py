# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from datetime import datetime, timedelta


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
        related="template.is_web_subscription",
        readonly=True,
    )

    @api.model
    def close_web_only_subscriptions(self):
        today = fields.Date.to_string((datetime.today()))

        subscriptions = self.search(
            [
                ("state", "=", "ongoing"),
                ("counter", "=", 0),
                ("end_date", "<", today),
            ]
        )

        subscriptions.write({"state": "terminated"})


class ProductSubscriptionRequest(models.Model):
    _inherit = "product.subscription.request"

    is_web_subscription = fields.Boolean(
        related="subscription_template.is_web_subscription"
    )
    websubscriber = fields.Many2one(
        comodel_name="res.partner",
        string="Web Subscriber",
        help=(
            "The websubscriber is the partner receiving the web access "
            "to medor online."
        ),
        required=True,
    )

    @api.multi
    def validate_request(self):
        super(ProductSubscriptionRequest, self).validate_request()
        self.websubscriber.compute_is_web_subscribed()
