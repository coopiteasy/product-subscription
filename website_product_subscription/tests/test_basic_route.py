# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from common import BaseProductSubscriptionCase
import form_data
import logging

_logger = logging.getLogger(__name__)


class TestBasicRoute(BaseProductSubscriptionCase):

    def test_new_subscription_basic_route_person(self):
        route = "/new/subscription/basic"

        data = form_data.SR_POST_DATA_BASIC_PERSON
        token = self.csrf_token(route)
        data["csrf_token"] = token

        response = self.http_post(route, data=data)
        self.assertEquals(response.status_code, 200)
        alert = self.get_alert(response)
        self.assertFalse(bool(alert), alert)
        title = self.html_doc(response).xpath("//title")[0].text
        self.assertIn("Product Subscription Thanks", title)

    def test_new_subscription_basic_route_company(self):
        route = "/new/subscription/basic"

        data = form_data.SR_POST_DATA_BASIC_COMPANY
        token = self.csrf_token(route)
        data["csrf_token"] = token

        response = self.http_post(route, data=data)
        self.assertEquals(response.status_code, 200)
        alert = self.get_alert(response)
        self.assertFalse(bool(alert), alert)
        title = self.html_doc(response).xpath("//title")[0].text
        self.assertIn("Product Subscription Thanks", title)

    def test_new_subscription_basic_route_company_invoice(self):
        route = "/new/subscription/basic"

        data = form_data.SR_POST_DATA_BASIC_COMPANY_INVOICE
        token = self.csrf_token(route)
        data["csrf_token"] = token

        response = self.http_post(route, data=data)
        self.assertEquals(response.status_code, 200)
        alert = self.get_alert(response)
        self.assertFalse(bool(alert), alert)
        title = self.html_doc(response).xpath("//title")[0].text
        self.assertIn("Product Subscription Thanks", title)
