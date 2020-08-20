# -*- coding: utf-8 -*-
import logging
from openerp import api, models

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    def _get_shipping_country(self, countries):
        country_ids = set()
        # values['shipping_countries'] = values['countries']

        delivery_carriers = self.search([("shipping_enabled", "=", True)])
        for carrier in delivery_carriers:
            if not carrier.country_ids:
                return False
            # Authorized shipping countries
            country_ids = country_ids | set(carrier.country_ids.ids)

        shipping_countries = countries.filtered(
            lambda r: r.id in list(country_ids)
        )
        return shipping_countries
