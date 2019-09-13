# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRLfs <http://coopiteasy.be>
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import http
from openerp.exceptions import ValidationError
from openerp.http import request
from openerp.tools.translate import _

from openerp.addons.website_product_subscription.controllers.subscribe_form import SubscribeForm


class SubscribeController(http.Controller):

    @http.route(
        '/new/subscription/basic',
        type='http',
        auth='public',
        website=True
    )
    def subscribe(self, **kwargs):
        self.subscribe_form_validation()
        if ('error' not in request.params
                and request.httprequest.method == 'POST'):
            sub_req = self.process_subscribe_form()
            values = {
                'subscription_request_id': sub_req,
                'subscriber': sub_req.subscriber.id,
                'subscription_template': sub_req.subscription_template.id,
                'gift': 'off',
                'sponsor': sub_req.sponsor.id if sub_req.sponsor else '',
            }
            # Template to render thanks
            kwargs['view_callback'] = (
                "website_product_subscription.product_subscription_thanks"
            )
            return self.get_subscription_response(values, kwargs)
        return request.website.render(
            'website_product_subscription.subscribe_form', request.params
        )

    @http.route(
        '/new/subscription/gift',
        type='http',
        auth='public',
        website=True
    )
    def gift_subscribe(self, **kwargs):
        self.gift_subscribe_form_validation()
        if ('error' not in request.params
                and request.httprequest.method == 'POST'):
            sub_req = self.process_gift_subscribe_form()
            values = {
                'subscription_request_id': sub_req,
                'subscriber': sub_req.subscriber.id,
                'subscription_template': sub_req.subscription_template.id,
                'gift': 'on',
                'sponsor': sub_req.sponsor.id if sub_req.sponsor else '',
            }
            # Template to render thanks
            kwargs['view_callback'] = (
                "website_product_subscription.product_subscription_thanks"
            )
            return self.get_subscription_response(values, kwargs)
        return request.website.render(
           'website_product_subscription.subscribe_gift_form', request.params
        )

    def subscribe_form_validation(self):
        """Execute form check and validation"""
        user = None
        if request.session.uid:
            user = request.env['res.users'].browse(request.session.uid)
        form = SubscribeForm(request.params, user, confirm=(not user))
        form.normalize_form_data()
        form.validate_form()
        form.init_form_data()
        self.fill_values(request.params)
        if request.httprequest.method == 'GET':
            form.set_form_defaults()

    def gift_subscribe_form_validation(self):
        """Execute form check and validation"""
        user = None
        if request.session.uid:
            user = request.env['res.users'].browse(request.session.uid)
        form = SubscribeForm(request.params, user, confirm=(not user))
        form.normalize_form_data()
        form.validate_form()
        form.init_form_data()
        self.fill_values(request.params)
        if request.httprequest.method == 'GET':
            form.set_form_defaults()

    def process_subscribe_form(self):
        params = request.params
        partner_obj = request.env['res.partner']
        partner_keys = [
            'firstname',
            'lastname',
            'login',
            'street',
            'zip',
            'city',
            'country_id',
        ]
        # Sponsor
        if params.get('is_company', False):
            # Company
            if request.session.uid:
                company = request.env.user.parent_id
            else:
                company_values = {
                    'customer': True,
                    'company_type': 'company',
                    'vat':  params['vat'],
                    'email': params['login'],
                }
                for key in partner_keys:
                    company_values[key] = params[key]
                company = partner_obj.sudo().create(company_values)
            params['company_id'] = company.id if company else False
            # Representative
            if request.session.uid:
                representative = request.env.user.partner_id
            else:
                repr_values = {
                    'parent_id': company.id,
                    'customer': True,
                    'company_type': 'person',
                    'vat':  params['vat'],
                    'email': params['login'],
                    'type': 'representative',
                }
                for key in partner_keys:
                    repr_values[key] = params[key]
                representative = partner_obj.sudo().create(repr_values)
            params['representative_id'] = (
                representative.id if representative else False
            )
            params['sponsor_id'] = (
                representative.id if representative else False
            )
        else:
            if request.session.uid:
                sponsor = request.env.user.partner_id
            else:
                sponsor_values = {
                    'name': params['firstname'] + ' ' + params['lastname'],
                    'email': params['login'],
                    'customer': True,
                }
                for key in partner_keys:
                    sponsor_values[key] = params[key]
                sponsor = partner_obj.sudo().create(sponsor_values)
            params['sponsor_id'] = sponsor.id if sponsor else False

        params['subscriber_id'] = params['sponsor_id']

        sub_req = self.create_subscription_request(params, gift=False)
        params['sub_req_id'] = sub_req.id

        if not request.session.uid:
            # Create webaccess
            self.create_user({
                'login': params['login'],
                'partner_id': params['sponsor_id'],
            })
        return sub_req

    def process_gift_subscribe_form(self):
        params = request.params
        partner_obj = request.env['res.partner']
        # TODO: Explicitly define each keys for company, sponsor,
        # subscriber. It will be clearer.
        partner_keys = [
            'firstname',
            'lastname',
            'login',
            'street',
            'zip',
            'city',
            'country_id',
        ]
        # Sponsor
        if params.get('is_company', False):
            # Company
            if request.session.uid:
                company = request.env.user.parent_id
            else:
                company_values = {
                    'customer': True,
                    'company_type': 'company',
                    'vat':  params['vat'],
                    'email': params['login'],
                }
                for key in partner_keys:
                    company_values[key] = params.get(key, False)
                company = partner_obj.sudo().create(company_values)
            params['company_id'] = company.id if company else False
            # Representative
            if request.session.uid:
                representative = request.env.user.partner_id
            else:
                repr_values = {
                    'parent_id': company.id,
                    'customer': True,
                    'company_type': 'person',
                    'vat':  params['vat'],
                    'email': params['login'],
                    'type': 'representative',
                }
                for key in partner_keys:
                    repr_values[key] = params.get(key, False)
                representative = partner_obj.sudo().create(repr_values)
            params['representative_id'] = (
                representative.id if representative else False
            )
            params['sponsor_id'] = (
                representative.id if representative else False
            )
        else:
            if request.session.uid:
                sponsor = request.env.user.partner_id
            else:
                sponsor_values = {
                    'name': params['firstname'] + ' ' + params['lastname'],
                    'email': params['login'],
                    'customer': True,
                }
                for key in partner_keys:
                    sponsor_values[key] = params.get(key, False)
                sponsor = partner_obj.sudo().create(sponsor_values)
            params['sponsor_id'] = sponsor.id if sponsor else False

        # Subscriber
        subscriber_values = {
            'company_type': 'person',
            'email': params['subscriber_login'],
        }
        for key in partner_keys:
            subscriber_values[key] = params['subscriber_'+key]
        subscriber = partner_obj.sudo().create(subscriber_values)
        params['subscriber_id'] = subscriber.id if subscriber else False

        sub_req = self.create_subscription_request(params, gift=True)
        params['sub_req_id'] = sub_req.id

        # Create webaccess
        self.create_user({
            'login': params['subscriber_login'],
            'partner_id': params['subscriber_id'],
        })
        return sub_req

    def fill_values(self, params, load_from_user=False):
        """Kept for compatibility reason."""
        return params

    def get_subscription_request_values(self, params, gift):
        vals = {
            'subscriber': params.get('subscriber_id'),
            'subscription_template': int(params.get('subscription')),
            'type': 'gift' if gift else 'basic',
            'sponsor': params.get('sponsor_id'),
        }
        return vals

    def create_subscription_request(self, params, gift):
        vals = self.get_subscription_request_values(params, gift)
        sub_request = (
            request.env['product.subscription.request']
            .sudo()
            .create(vals)
        )
        return sub_request

    def create_user(self, user_values):
        sudo_users = request.env['res.users'].sudo()
        user_id = sudo_users._signup_create_user(user_values)
        user = sudo_users.browse(user_id)
        user.with_context({'create_user': True}).action_reset_password()
        return user_id

    def get_subscription_response(self, values, kw):
        values = self.preRenderThanks(values, kw)
        return request.website.render(
            'website_product_subscription.product_subscription_thanks',
            values
        )

    def preRenderThanks(self, values, kwargs):
        """
        Use this function to fill context givent to render of the
        thanks response.
        """
        return {
            '_values': values,
            '_kwargs': kwargs,
            # Give redirect object to success page
            'redirect': kwargs.get('redirect', ''),
        }
