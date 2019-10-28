# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from openerp import fields


class TestProductSubscription(TransactionCase):
    def test_subscription_flow(self):
        request_id = self.ref(
            "product_subscription.demo_product_subscription_request_1"
        )  # noqa
        request = self.env["product.subscription.request"].browse(request_id)

        request.validate_request()
        self.assertEqual(request.state, "sent")
        request.invoice.confirm_paid()
        self.assertEqual(request.state, "paid")

        subscription = request.subscription
        self.assertEqual(subscription.state, "ongoing")
        self.assertEqual(subscription.subscribed_on, fields.Date.today())

    def test_request_for_free_subscription(self):
        journal = self.env.ref(
            "product_subscription.demo_product_subscription_journal"
        )
        categ = self.env.ref("product.product_category_3")
        uom = self.env.ref("product.product_uom_unit")
        partner = self.env.ref("product_subscription.demo_subscriber_4")

        life_product = self.env["product.template"].create(
            {
                "name": "lifelong product",
                "categ_id": categ.id,
                "sale_ok": True,
                "list_price": 0,
                "type": "service",
                "uom_id": uom.id,
                "subscription": True,
                "product_qty": 4,
            }
        )

        life_subscription = self.env["product.subscription.template"].create(
            {
                "name": "lifelong subscription",
                "product_qty": 100,
                "price": 0,
                "product": life_product.id,
                "journal": journal.id,
            }
        )

        request = self.env["product.subscription.request"].create(
            {
                "subscriber": partner.id,
                "sponsor": partner.id,
                "subscription_template": life_subscription.id,
            }
        )

        request.validate_request()

        self.assertEquals(request.invoice.state, "paid")
        self.assertTrue(request.subscription)
        self.assertEquals(request.subscription.state, "ongoing")
        self.assertTrue(len(partner.subscriptions) > 0)
