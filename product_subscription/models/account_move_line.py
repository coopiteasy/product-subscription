# -*- coding: utf-8 -*-
# Copyright 2020 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import models, api


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.multi
    def remove_move_reconcile(self):
        for account_move_line in self:
            for invoice in account_move_line.payment_id.invoice_ids:
                if (invoice.id == self.env.context.get('invoice_id')
                   and account_move_line in invoice.payment_move_line_ids
                   and invoice.subscription):
                    sub = invoice.product_subscription_request[0].subscription
                    sub.action_cancel()
        return super(AccountMoveLine, self).remove_move_reconcile()
