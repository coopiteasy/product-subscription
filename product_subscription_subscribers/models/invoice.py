# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def process_subscription(self, effective_date):
        res = super(AccountInvoice, self).process_subscription(effective_date)
        request = self.product_subscription_request
        subscription = request.subscription
        subscription.additional_subscribers = request.additional_subscribers
        return res
