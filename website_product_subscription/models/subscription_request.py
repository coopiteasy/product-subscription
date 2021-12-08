# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import datetime
import logging

from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class SubscriptionRequest(models.Model):
    _inherit = "product.subscription.request"

    @api.multi
    def validate_request(self):
        res = super(SubscriptionRequest, self).validate_request()
        for request in self:
            if not request.gift_sent:
                request.send_gift_emails()
            if not request.subscriber.has_web_access():
                request.create_web_access()
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
        now = fields.Datetime.from_string(fields.Datetime.now()).time()
        if now < datetime.time(7, 0, 0) or now > datetime.time(22, 0, 0):
            # Don't send e-mails during hours meant for sleep.
            _logger.info(
                "Skipping cron_create_scheduled_gift_user because it's late: %s"
                % now
            )
            return

        requests = self.search(
            [
                ("gift", "=", True),
                ("gift_sent", "=", False),
                # TODO: Revert following back to '<=' once the back log has
                # cleared. (T3833)
                ("gift_date", "=", fields.Date.today()),
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
