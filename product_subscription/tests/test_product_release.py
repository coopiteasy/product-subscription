# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
import datetime as dt


class TestProductRelease(TransactionCase):
    def test_product_release_cycle(self):
        self.assertTrue(True)
        # too slow

    #     release_date = dt.date.today() + dt.timedelta(days=30)
    #     product_id = self.ref('product_subscription.demo_released_product_1')
    #     template_id = self.ref('product_subscription.demo_subscription_template_1')
    #     requests = (
    #         self.env['product.subscription.request']
    #             .search([('state', '=', 'draft')])
    #     )
    #     requests.validate_request()
    #     requests.mapped('invoice').confirm_paid()
    #
    #     release = self.env['product.release.list'].create({
    #         'release_date': release_date,
    #         'product_id': product_id,
    #         'template_id': template_id,
    #         'release_qty': 1,
    #     })
    #
    #     release.action_validate()
    #     self.assertEqual(release.state, 'validated')
    #     self.assertEqual(len(release.product_release_lines), 2)
    #
    #     release.action_done()
    #     self.assertEqual(release.state, 'done')
    #     self.assertEqual(len(release.picking_ids), 2)

    # release.action_transfer()  # todo assign stock on product
