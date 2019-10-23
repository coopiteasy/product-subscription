# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestProductSubscriptionWebAccess(TransactionCase):
    def test_basic_subscription_gives_web_access(self):
        partner = self.env.ref("base.res_partner_address_26")
        template = self.env.ref(
            "product_subscription.demo_subscription_template_1"
        )

        self.env["ir.config_parameter"].set_param(
            "product_subscription_web_access.temporary_access_length", str(30)
        )

        self.assertFalse(partner.subscriber)
        self.assertFalse(partner.is_web_subscribed)

        request = self.env["product.subscription.request"].create(
            {
                "type": "basic",
                "subscriber": partner.id,
                "sponsor": partner.id,
                "websubscriber": partner.id,
                "subscription_template": template.id,
            }
        )

        self.assertFalse(partner.subscriber)
        self.assertFalse(partner.is_web_subscribed)

        request.validate_request()
        self.assertFalse(partner.subscriber)
        self.assertTrue(partner.is_web_subscribed)

        request.invoice.confirm_paid()
        self.assertTrue(partner.subscriber)
        self.assertTrue(partner.is_web_subscribed)

        subscription = request.subscription
        subscription.counter = 0
        subscription.state = "terminated"

        self.assertFalse(partner.subscriber)
        self.assertTrue(partner.is_web_subscribed)
