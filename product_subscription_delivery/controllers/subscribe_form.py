# -*- coding: utf-8 -*-

from openerp.http import request
from openerp.addons.website_product_subscription.controllers.subscribe_form import (
    SubscribeForm,
)


class DeliverySubscribeForm(SubscribeForm):
    def get_countries(self):
        countries = super(DeliverySubscribeForm, self).get_countries()
        shipping_countries = (
            request.env["delivery.carrier"]
            .sudo()
            ._get_shipping_country(countries)
        )
        return shipping_countries
