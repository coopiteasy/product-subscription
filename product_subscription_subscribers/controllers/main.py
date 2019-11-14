# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request
from openerp.tools.translate import _

from openerp.addons.website_product_subscription.controllers.main import (
    WebsiteProductSubscription,
)
from openerp.addons.website_product_subscription.controllers.subscribe import (
    SubscribeController,
)


def create_additional_subscriber(email, subscriber):
    partner = request.env["res.partner"].sudo().search([("email", "=", email)])
    if partner:
        partner.parent_id = subscriber
        return partner[0]
    else:
        partner = (
            request.env["res.partner"]
            .sudo()
            .create(
                {
                    "name": email,
                    "email": email,
                    "customer": True,
                    "parent_id": subscriber.id,
                }
            )
        )
        return partner


def add_subscribers_to_subscription(subscription, params):
    subscribers = [
        v for k, v in params.items() if k.startswith("additionnal_email") and v
    ]

    additional_subscriber_ids = [
        create_additional_subscriber(email, subscription.subscriber).id  # noqa
        for email in subscribers
    ]
    subscription.write(
        {"additional_subscribers": [(6, _, additional_subscriber_ids)]}
    )

    return subscription


class WebsiteProductSubscriptionSubscribers(WebsiteProductSubscription):
    def fill_values(self, values, load_from_user=False):
        values = super(
            WebsiteProductSubscriptionSubscribers, self
        ).fill_values(values, load_from_user)
        if load_from_user and request.env.user.login != "public":
            emails = request.env.user.partner_id.child_ids.mapped("email")
            additionnal_subscribers = {
                "additionnal_email_%s" % (i + 1): email
                for i, email in enumerate(emails)
            }
        else:
            additionnal_subscribers = {
                "additionnal_email_1": values.get("additionnal_email_1", ""),
                "additionnal_email_2": values.get("additionnal_email_2", ""),
                "additionnal_email_3": values.get("additionnal_email_3", ""),
                "additionnal_email_4": values.get("additionnal_email_4", ""),
                "additionnal_email_5": values.get("additionnal_email_5", ""),
                "additionnal_email_6": values.get("additionnal_email_6", ""),
            }

        values.update(additionnal_subscribers)
        return values

    def create_subscription_request(self, **kwargs):
        subscription = super(
            WebsiteProductSubscriptionSubscribers, self
        ).create_subscription_request(**kwargs)

        return add_subscribers_to_subscription(subscription, kwargs)


class SubscribeControllerSubscribers(SubscribeController):
    def process_new_subscription_basic_form(self):
        subscription = super(
            SubscribeControllerSubscribers, self
        ).process_new_subscription_basic_form()

        return add_subscribers_to_subscription(subscription, request.params)

    def process_new_subscription_gift_form(self):
        subscription = super(
            SubscribeControllerSubscribers, self
        ).process_new_subscription_gift_form()

        return add_subscribers_to_subscription(subscription, request.params)
