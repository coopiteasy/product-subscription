# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class SubscriptionRequest(models.Model):
    _inherit = "product.subscription.request"

    @api.multi
    def validate_request(self):
        res = super(SubscriptionRequest, self).validate_request()
        self.create_web_access()
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
            if self.env["res.users"].user_exists(request.subscriber.email):
                existing_user_template.send_mail(request.id)
            else:
                new_user_template.send_mail(request.id)
                request.subscriber.create_web_access()
            request.gift_sent = True

    @api.multi
    def create_web_access(self):
        today = fields.Date.today()
        for request in self:
            if request.type == "gift" and request.gift_date <= today:
                request.send_gift_emails()
            elif request.type == "gift" and request.gift_date > today:
                continue
            else:
                request.subscriber.create_web_access()

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
        requests.send_gift_emails()
