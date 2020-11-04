# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class SubscriptionRequest(models.Model):
    _inherit = "product.subscription.request"

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
            partner = request.subscriber
            User = self.env["res.users"]

            if not User.user_exist(partner.email):
                User.create_user(
                    {"login": partner.email, "partner_id": partner.id}
                )
            request.gift_sent = True

            # fixme if beneficiary exists, no mail is sent and the user won't know he was subscribed
