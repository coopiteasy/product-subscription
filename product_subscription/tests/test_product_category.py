# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Carmen Bianca Bakker <carmen@carmenbianca.eu>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from openerp.tests.common import TransactionCase
from openerp import fields


class TestSubscriptionCategories(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super(TestSubscriptionCategories, self).setUp(*args, **kwargs)

        self.medor_template_1 = self.env.ref("product_subscription.demo_subscription_template_1")
        self.medor_template_2 = self.env.ref("product_subscription.demo_subscription_template_3")
        self.alter_template = self.env.ref("product_subscription.demo_subscription_template_2")

        # Already subscribed to self.alter_template
        self.subscriber = self.env.ref("product_subscription.demo_subscriber_3")

        return result

    def test_start_date_different_subscription(self):
        """When adding a new subscription (of a different category) to an
        existing subscriber, the start date should be now, and not after the end
        of the existing subscription.
        """
        # Start with one subscription on Alter.
        self.assertEqual(len(self.subscriber.subscriptions), 1)

        new_request = self.env["product.subscription.request"].create(
            {
                "subscriber": self.subscriber.id,
                "sponsor": self.subscriber.id,
                "subscription_template": self.medor_template_1.id,
            }
        )

        new_request.validate_request()
        new_request.invoice.confirm_paid()

        new_subscription = new_request.subscription

        # One additional subscription on Médor.
        self.assertEqual(len(self.subscriber.subscriptions), 2)
        self.assertIn(new_subscription, self.subscriber.subscriptions)
        # New subscription starts today.
        self.assertEqual(new_subscription.start_date, fields.Date.today())
