# -*- coding: utf-8 -*-
# Copyright 2020 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import models, api


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.multi
    def remove_move_reconcile(self):
        # when a subscription invoice is unreconcilled
        # we cancel the corresponding subscription
        # and we set back subscription request state to sent.
        for aml in self:
            invoice = aml.matched_debit_ids.debit_move_id.invoice_id
            if (aml in invoice.payment_move_line_ids
               and invoice.subscription):
                sub_req = invoice.product_subscription_request[0]
                if sub_req.subscription:
                    sub_req.subscription.action_cancel()
                sub_req.state = 'sent'
        return super(AccountMoveLine, self).remove_move_reconcile()
