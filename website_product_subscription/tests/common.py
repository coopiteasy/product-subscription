# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from lxml import html
from openerp.tests.common import TransactionCase, HttpCase
import json
import requests
from .. import controllers

_logger = logging.getLogger(__name__)

HOST = "127.0.0.1"
PORT = "9999"  # fixme find dynamically


class BaseProductSubscriptionCase(HttpCase):
    def setUp(self):
        super(BaseProductSubscriptionCase, self).setUp()
        self.session = requests.Session()

        def patch_check_recaptcha(self, **kwargs):
            logging.info("info patching check_recaptcha: skip")

        controllers.subscribe_form.SubscribeForm._validate_recaptcha = (
            patch_check_recaptcha
        )

    def http_get(self, url, headers=None):
        if url.startswith("/"):
            url = "http://%s:%s%s" % (HOST, PORT, url)

        return self.session.get(url, headers=headers)

    def http_get_content(self, route, headers=None):
        response = self.http_get(route, headers=headers)
        self.assertEquals(response.status_code, 200)

        return json.loads(response.content)

    def http_post(self, url, data, headers=None):
        if url.startswith("/"):
            url = "http://%s:%s%s" % (HOST, PORT, url)

        response = self.session.post(url, data=data, headers=headers)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(
            "Odoo Server Error" in response.text,
            "Server returned jsonrpc Odoo Server Error",
        )
        return response

    @staticmethod
    def html_doc(response):
        """Get an HTML LXML document."""
        return html.fromstring(response.content)

    def login(self, login, password):
        url = "/web/login"
        response = self.http_get(url)
        self.assertEquals(response.status_code, 200)

        doc = self.html_doc(response)
        token = doc.xpath("//input[@name='csrf_token']")[0].get("value")

        response = self.http_post(
            url=url,
            data={"login": login, "password": password, "csrf_token": token},
        )
        self.assertEquals(response.status_code, 200)
        return response

    def csrf_token(self, url=None):
        """Get a valid CSRF token."""
        if url is None:
            url = "/web/"

        response = self.http_get(url)
        doc = self.html_doc(response)
        return doc.xpath("//input[@name='csrf_token']")[0].get("value")

    def get_alert(self, response):
        danger = self.html_doc(response).xpath(
            "//div[contains(@class, 'alert-danger')]"
        )
        if danger:
            return danger[0].text.strip()
        else:
            return None
