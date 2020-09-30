# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from lxml import html
from openerp.tests.common import HttpCase
from werkzeug.test import Client
from openerp.service import wsgi_server
from werkzeug.wrappers import BaseResponse


from openerp.addons.website_product_subscription.tests.test_generic_route import (
    TestGenericRoute,
)

_logger = logging.getLogger(__name__)


SR_POST_DATA_GENERIC_ADDITIONAL_DATA = {
    "firstname": u"Enrique",
    "lastname": u"Jones",
    "login": u"enrique@jones.org",
    "confirm_login": u"enrique@jones.org",
    "street": u"Some street",
    "zip_code": u"09876",
    "city": u"bxl",
    "country_id": u"21",  # todo do better
    "subscription": u"1",  # todo do better
    "accepted_condition": "on",
    "additional_email_1": "pierre@survivor.be",
    "additional_email_2": "vincent@startup.be",
}


class TestAdditionalSubscribers(TestGenericRoute):
    def test_subscribe_additional_subscribers(self):
        route = "/new/subscription/generic"

        data = SR_POST_DATA_GENERIC_ADDITIONAL_DATA
        token = self.csrf_token(route)
        data["csrf_token"] = token

        response = self.http_post(route, data=data)
        self.assertEquals(response.status_code, 200)
        alert = self.get_alert(response)
        self.assertFalse(bool(alert), alert)
        title = self.html_doc(response).xpath("//title")[0].text
        self.assertIn("Product Subscription Thanks", title)
