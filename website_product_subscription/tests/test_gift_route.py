# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from common import BaseProductSubscriptionCase
import form_data
import logging

_logger = logging.getLogger(__name__)


class TestGiftRoute(BaseProductSubscriptionCase):
    def test_legacy_routes_subscriber_route(self):
        response = self.http_get("/login_subscriber")
        self.assertEquals(response.status_code, 200)
        response = self.http_get("/page/login_subscriber")
        self.assertEquals(response.status_code, 200)
        response = self.http_get("/become_subscriber")
        self.assertEquals(response.status_code, 200)
        response = self.http_get("/page/become_subscriber")
        self.assertEquals(response.status_code, 200)

    def test_new_subscription_gift_route_person(self):
        route = "/new/subscription/gift"

        data = form_data.SR_POST_DATA_GIFT_PERSON
        token = self.csrf_token(route)
        data["csrf_token"] = token

        response = self.http_post(route, data=data)
        self.assertEquals(response.status_code, 200)
        alert = self.get_alert(response)
        self.assertFalse(bool(alert), alert)
        title = self.html_doc(response).xpath("//title")[0].text
        self.assertIn("Product Subscription Thanks", title)

    def test_new_subscription_gift_route_company(self):
        route = "/new/subscription/gift"

        data = form_data.SR_POST_DATA_GIFT_COMPANY
        token = self.csrf_token(route)
        data["csrf_token"] = token

        response = self.http_post(route, data=data)
        self.assertEquals(response.status_code, 200)
        alert = self.get_alert(response)
        self.assertFalse(bool(alert), alert)
        title = self.html_doc(response).xpath("//title")[0].text
        self.assertIn("Product Subscription Thanks", title)
