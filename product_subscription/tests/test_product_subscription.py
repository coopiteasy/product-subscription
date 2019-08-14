# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestProductSubscription(TransactionCase):

    def test_confirm_paid_sets_additionnal_addresses(self):
        request_id = self.ref('product_subscription.demo_product_subscription_request_1')  # noqa
        request = self.env['product.subscription.request'].browse(request_id)

        request.validate_request()
        self.assertEqual(request.state, 'sent')
        request.invoice.confirm_paid()
        self.assertEqual(request.state, 'paid')

        subscription = request.subscription
        self.assertEqual(subscription.state, 'ongoing')
