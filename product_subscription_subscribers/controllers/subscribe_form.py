# -*- coding: utf-8 -*-
# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.addons.website_product_subscription.controllers.subscribe_form import (
    SubscribeForm,
)


class AdditionalSubscribeForm(SubscribeForm):
    def validate_form(self):
        super(AdditionalSubscribeForm, self).validate_form()
        fields = [
            "additional_email_1",
            "additional_email_2",
            "additional_email_3",
            "additional_email_4",
            "additional_email_5",
            "additional_email_6",
        ]
        for field in fields:
            if self.qcontext.get(field):
                email = self.qcontext.get(field)
                self._validate_email_format(email)
