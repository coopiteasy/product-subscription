# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DTF
from datetime import date, datetime


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_web_subscribed = fields.Boolean(
        string='Is Web Subscribed',
        compute='_compute_is_web_subscribed',
        store=True)

    @api.multi
    @api.depends('subscriptions.state',
                 'subscriptions.subscribed_on',
                 'subscriptions.end_date',
                 'subscriptions.is_web_subscription')
    def _compute_is_web_subscribed(self):
        for partner in self:
            subscriptions = (
                partner.subscriptions.filtered(
                    lambda s: s.state in ['renew', 'ongoing'] and s.is_web_subscription  # noqa
            ))

            if subscriptions:
                first = subscriptions.sorted(lambda s: s.subscribed_on)[0]
                last = subscriptions.sorted(lambda s: s.end_date, reverse=True)[0]

                start = datetime.strptime(first.subscribed_on, DTF)
                end = datetime.strptime(last.end_date, DTF)

                if start <= datetime.now() <= end:
                    partner.is_web_subscribed = True
                else:
                    partner.is_web_subscribed = False
            else:
                partner.is_web_subscribed = False