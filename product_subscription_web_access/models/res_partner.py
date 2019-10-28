# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DTF
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


def _pd(dt):
    """parse datetime"""
    return datetime.strptime(dt, DTF) if dt else dt


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_web_subscribed = fields.Boolean(
        string="Is Web Subscribed",
        compute="compute_is_web_subscribed",
        store=True,
    )

    @api.multi
    @api.depends(
        "subscriptions.state",
        "subscriptions.start_date",
        "subscriptions.end_date",
        "subscriptions.is_web_subscription",
    )
    def compute_is_web_subscribed(self):
        for partner in self:
            subscriptions = partner.subscriptions.filtered(
                lambda s: s.state in ["renew", "ongoing", "terminated"]
                and s.is_web_subscription
            )
            today = datetime.today()
            temp_access = self.env["website"].browse(1).temporary_access_length
            temp_access_limit = fields.Date.to_string(
                today - timedelta(days=temp_access)
            )
            open_requests = self.env["product.subscription.request"].search(
                [
                    ("state", "=", "sent"),
                    ("is_web_subscription", "=", True),
                    ("websubscriber", "=", partner.id),
                    ("subscription_date", ">=", temp_access_limit),
                ]
            )

            if open_requests:
                partner.is_web_subscribed = True
            elif subscriptions:
                first = subscriptions.sorted(lambda s: s.start_date)[0]
                last = subscriptions.sorted(
                    lambda s: s.end_date, reverse=True
                )[0]

                start = _pd(first.start_date)
                end = _pd(last.end_date)

                if start <= datetime.now() <= end:
                    partner.is_web_subscribed = True
                else:
                    partner.is_web_subscribed = False
            else:
                partner.is_web_subscribed = False

    @api.model
    def cron_update_is_web_subscribed(self):
        partners = self.env["res.partner"].search([])
        _logger.info(
            "launch cron_update_is_web_subscribed on %s partners"
            % len(partners)
        )
        partners.compute_is_web_subscribed()
