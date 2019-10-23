# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DTF
from datetime import datetime, timedelta


def _pd(dt):
    """parse datetime"""
    return datetime.strptime(dt, DTF) if dt else dt


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_web_subscribed = fields.Boolean(
        string="Is Web Subscribed",
        compute="_compute_is_web_subscribed",
        store=True,
    )

    @api.multi
    @api.depends(
        "subscriptions.state",
        "subscriptions.start_date",
        "subscriptions.end_date",
        "subscriptions.is_web_subscription",
        "requests.state",
    )
    def _compute_is_web_subscribed(self):
        for partner in self:
            subscriptions = partner.subscriptions.filtered(
                lambda s: s.state in ["renew", "ongoing", "terminated"]
                and s.is_web_subscription
            )
            today = datetime.today()
            temp_access = int(
                self.env["ir.config_parameter"].get_param(
                    "product_subscription_web_access"
                    ".temporary_access_length"
                )
            )
            open_requests = partner.requests.filtered(
                lambda r: r.state == "sent"
                and r.is_web_subscription
                and today
                <= _pd(r.subscription_date) + timedelta(days=temp_access)
            )

            if subscriptions:
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
            elif open_requests:
                partner.is_web_subscribed = True
            else:
                partner.is_web_subscribed = False
