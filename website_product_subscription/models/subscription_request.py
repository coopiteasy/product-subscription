# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class SubscriptionRequest(models.Model):
    _inherit = "product.subscription.request"

    @api.multi
    def validate_request(self):
        res = super(SubscriptionRequest, self).validate_request()
        today = fields.Date.today()
        for request in self:
            if (
                request.type != "gift"
                or (not request.gift_sent and request.gift_date <= today)
            ):
                request.send_gift_emails()
                request.subscriber.create_web_access()
        return res

    @api.multi
    def send_gift_emails(self):
        new_user_template = self.env.ref(
            "website_product_subscription"
            ".gift_subscription_new_user_mail_template"
        )
        existing_user_template = self.env.ref(
            "website_product_subscription"
            ".gift_subscription_existing_user_mail_template"
        )
        for request in self:
            if (
                request.gift_sent
                or request.type != "gift"
                or request.gift_date > fields.Date.today()
            ):
                # Don't send an e-mail (again, at all, or yet, in that order).
                continue
            if not request.subscriber.email:
                _logger.error(
                    "partner %s %s does not have an email address; cannot send gift email"
                    % (request.subscriber.id, request.subscriber.name)
                )
                continue
            if request.subscriber.has_web_access():
                template = existing_user_template
            else:
                template = new_user_template
            template.send_mail(request.id)
            request.gift_sent = True

    @api.model
    def cron_create_scheduled_gift_user(self):
        today = fields.Date.today()
        requests = self.search(
            [
                ("gift", "=", True),
                ("gift_sent", "=", False),
                ("gift_date", "<=", today),
            ]
        )
        for request in requests:
            try:
                request.send_gift_emails()
                request.subscriber.create_web_access()
            except Exception:
                _logger.exception(
                    "cron_create_scheduled_gift_user failed for request %s"
                    % request.id
                )
