# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from openerp import fields


class TestProductSubscription(TransactionCase):

    def test_create_request_to_manual_origin(self):
        journal = self.env.ref(
            'product_subscription.demo_product_subscription_journal')
        categ = self.env.ref('product.product_category_3')
        uom = self.env.ref('product.product_uom_unit')
        partner = self.env.ref('product_subscription.demo_subscriber_4')

        product = self.env['product.template'].create({
            'name': 'lifelong product',
            'categ_id': categ.id,
            'sale_ok': True,
            'list_price': 0,
            'type': 'service',
            'uom_id': uom.id,
            'subscription': True,
            'product_qty': 4,
        })

        subscription = self.env['product.subscription.template'].create({
            'name': 'lifelong subscription',
            'product_qty': 100,
            'price': 0,
            'product': product.id,
            'journal': journal.id,
        })

        request = self.env['product.subscription.request'].create({
            'subscriber': partner.id,
            'sponsor': partner.id,
            'subscription_template': subscription.id,
        })

        self.assertEquals(request.origin, 'manual')

        request.validate_request()

        self.assertTrue(request.payment_transaction)
        self.assertEquals(request.payment_transaction.payment_type, 'deferred')
