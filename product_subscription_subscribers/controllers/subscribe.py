# -*- coding: utf-8 -*-
# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from openerp.http import request
from openerp.tools.translate import _

from openerp.addons.website_product_subscription.controllers.subscribe import (
    SubscribeController,
)


class AdditionalSubscribeController(SubscribeController):
    def create_additional_subscriber(self, email):
        subscriber_id = request.params.get("subscriber_id")

        partner = (
            request.env["res.partner"].sudo().search([("email", "=", email)])
        )
        if partner:
            partner.write({"parent_id": subscriber_id})
            partner = partner[0]
        else:
            partner = (
                request.env["res.partner"]
                .sudo()
                .create(
                    {
                        "name": email,
                        "email": email,
                        "customer": True,
                        "parent_id": subscriber_id,
                    }
                )
            )
        return partner

    def create_subscription_request(self):
        sub_request = super(
            AdditionalSubscribeController, self
        ).create_subscription_request()

        params = request.params
        additional_subscribers = [
            params.get("additional_email_1", ""),
            params.get("additional_email_2", ""),
            params.get("additional_email_3", ""),
            params.get("additional_email_4", ""),
            params.get("additional_email_5", ""),
            params.get("additional_email_6", ""),
        ]
        additional_subscribers = filter(lambda el: el, additional_subscribers)

        additional_subscriber_ids = [
            self.create_additional_subscriber(email).id
            for email in additional_subscribers
        ]
        sub_request.write(
            {"additional_subscribers": [(6, _, additional_subscriber_ids)]}
        )

        return sub_request
