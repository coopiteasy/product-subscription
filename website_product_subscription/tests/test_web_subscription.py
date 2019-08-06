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


from .. import controllers

_logger = logging.getLogger(__name__)


class TestWebsiteProductSubscription(HttpCase):

    def setUp(self):
        super(TestWebsiteProductSubscription, self).setUp()

        with self.registry.cursor() as test_cursor:
            env = self.env(test_cursor)

            self.admin_password = 'AdminPa$$w0rd'
            env.ref('base.user_root').password = self.admin_password
            self.passkey_password = 'PasskeyPa$$w0rd'
            self.passkey_user = env['res.users'].create({
                'name': 'passkey',
                'login': 'passkey',
                'email': 'passkey',
                'password': self.passkey_password
            })
            self.dbname = env.cr.dbname

        self.werkzeug_environ = {'REMOTE_ADDR': '127.0.0.1'}
        self.test_client = Client(wsgi_server.application, BaseResponse)
        self.test_client.get('/web/session/logout')
        self.token = self.csrf_token()

        def patch_check_recaptcha(self, **kwargs):
            logging.info('info patch check_recaptcha to skip')

        controllers.main.WebsiteProductSubscription.check_recaptcha = patch_check_recaptcha

    def xpath(self, response, expr):
        return html.document_fromstring(response).xpath(expr)

    def get_request(self, url, data=None):
        return self.test_client.get(
            url, query_string=data, follow_redirects=True)

    def post_request(self, url=None, data=None, timeout=10):
        doc = self.test_client.post(url,
                                    data=data,
                                    environ_base=self.werkzeug_environ)
        return doc

    def html_doc(self, response):
        """Get an HTML LXML document."""
        return html.fromstring(response.data)

    def csrf_token(self):
        """Get a valid CSRF token."""
        response = self.get_request('/web/', data={'db': self.dbname})
        doc = self.html_doc(response)
        return doc.xpath("//input[@name='csrf_token']")[0].get('value')

    def login(self, username, password):
        # Login as demo user
        self.post_request('/web/login', data={
            'login': username,
            'password': password,
            'csrf_token': self.token,
        })
        self.logged_user = self.env['res.users'].search([
            ('login', '=', username)])
        return self.logged_user

    def test_subscribe_new_user(self):
        template = self.env.ref('product_subscription.demo_subscription_template_1')

        data = {
            'product_subscription_id': template.id,

            'firstname': u'Robin',
            'lastname': u'Desbois',
            'email': u'robin@desbois.coop',
            'email_confirmation': u'robin@desbois.coop',

            'subscriber_firstname': u'',
            'subscriber_lastname': u'',
            'subscriber_email': u'',

            'street': u"rue Fontaine d'Amour",
            'city': u'Bruxelles',
            'street_number': u'23',
            'box': u'',
            'zip_code': u'1030',
            'country_id': u'21',

            'company': u'',
            'vat_number': u'',

            'csrf_token': self.token,
            'g-recaptcha-response': u'xxx',
        }
        res = self.post_request('/product_subscription/subscribe', data)
        self.assertEqual(res.status_code, 200)

        doc = self.html_doc(res)
        alert_success = doc.xpath("//div[contains(@class, 'alert-success')]")
        self.assertTrue(len(alert_success) > 0)

    def test_subscribe_new_sponsor(self):
        template = self.env.ref('product_subscription.demo_subscription_template_1')

        data = {
            'product_subscription_id': template.id,

            'firstname': u'Robin',
            'lastname': u'Desbois',
            'email': u'robin@desbois.coop',
            'email_confirmation': u'robin@desbois.coop',

            'gift': u'on',
            'subscriber_firstname': u'robinet',
            'subscriber_lastname': u'des bosquet',
            'subscriber_email': u'robinet@desbosquet.coop',

            'street': u"rue Fontaine d'Amour",
            'city': u'Bruxelles',
            'street_number': u'23',
            'box': u'',
            'zip_code': u'1030',
            'country_id': u'21',

            'company': u'',
            'vat_number': u'',

            'csrf_token': self.token,
            'g-recaptcha-response': u'xxx',
        }
        res = self.post_request('/product_subscription/subscribe', data)
        self.assertEqual(res.status_code, 200)

        doc = self.html_doc(res)
        alert_success = doc.xpath("//div[contains(@class, 'alert-success')]")
        self.assertTrue(len(alert_success) > 0)

    def test_subscribe_logged_user(self):
        template = self.env.ref('product_subscription.demo_subscription_template_1')
        user = self.login('demo', 'demo')
        data = {
            'product_subscription_id': template.id,

            'firstname': u'Robin',
            'lastname': u'Desbois',
            'email': user.login,

            'subscriber_firstname': u'',
            'subscriber_lastname': u'',
            'subscriber_email': u'',

            'street': u"rue Fontaine d'Amour",
            'city': u'Bruxelles',
            'street_number': u'23',
            'box': u'',
            'zip_code': u'1030',
            'country_id': u'21',

            'company': u'',
            'vat_number': u'',

            'logged': u'on',
            'csrf_token': self.token,
            'g-recaptcha-response': u'xxx',
        }
        res = self.post_request('/product_subscription/subscribe', data)
        self.assertEqual(res.status_code, 200)

        doc = self.html_doc(res)
        alert_success = doc.xpath("//div[contains(@class, 'alert-success')]")
        self.assertTrue(len(alert_success) > 0)

    def test_subscribe_logged_sponsor(self):
        template = self.env.ref('product_subscription.demo_subscription_template_1')
        user = self.login('demo', 'demo')
        data = {
            'product_subscription_id': template.id,

            'firstname': u'Robin',
            'lastname': u'Desbois',
            'email': user.login,

            'gift': 'on',
            'subscriber_firstname': u'robinet',
            'subscriber_lastname': u'des bosquet',
            'subscriber_email': u'robinet@desbosquet.coop',

            'street': u"rue Fontaine d'Amour",
            'city': u'Bruxelles',
            'street_number': u'23',
            'box': u'',
            'zip_code': u'1030',
            'country_id': u'21',

            'company': u'',
            'vat_number': u'',

            'logged': 'on',
            'csrf_token': self.token,
            'g-recaptcha-response': u'xxx',
        }
        res = self.post_request('/product_subscription/subscribe', data)
        self.assertEqual(res.status_code, 200)

        doc = self.html_doc(res)
        alert_success = doc.xpath("//div[contains(@class, 'alert-success')]")
        self.assertTrue(len(alert_success) > 0)

    def test_different_confirmation_email(self):
        template = self.env.ref('product_subscription.demo_subscription_template_1')

        data = {
            'product_subscription_id': template.id,

            'firstname': u'Robin',
            'lastname': u'Desbois',
            'email': u'robin@desbois.coop',
            'email_confirmation': u'hector@desbois.coop',

            'csrf_token': self.token,
            'g-recaptcha-response': u'xxx',
        }
        res = self.post_request('/product_subscription/subscribe', data)
        self.assertEqual(res.status_code, 200)

        doc = self.html_doc(res)
        alert_danger = doc.xpath("//div[contains(@class, 'alert-danger')]")
        self.assertTrue(len(alert_danger) > 0)

    def test_subscribe_existing_email(self):
        template = self.env.ref('product_subscription.demo_subscription_template_1')

        data = {
            'product_subscription_id': template.id,

            'firstname': u'Robin',
            'lastname': u'Desbois',
            'email': u'passkey',
            'email_confirmation': u'passkey',

            'csrf_token': self.token,
            'g-recaptcha-response': u'xxx',
        }
        res = self.post_request('/product_subscription/subscribe', data)
        self.assertEqual(res.status_code, 200)

        doc = self.html_doc(res)
        alert_danger = doc.xpath("//div[contains(@class, 'alert-danger')]")
        self.assertTrue(len(alert_danger) > 0)
