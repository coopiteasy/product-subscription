# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request
from openerp.tools.translate import _


_PS_THANKS_TEMPLATE = 'website_product_subscription.product_subscription_thanks'
_BECOME_SUBSCRIBER_TEMPLATE = 'website_product_subscription.becomesubscriber'


class WebsiteProductSubscription(http.Controller):

    @http.route(['/subscription/field/presentation_text'],
                type='json',
                auth='public',
                methods=['POST'], website=True)
    def get_subscription_presentation_text(self, sub_template_id, **kw):
        sub_temp_obj = request.env['product.subscription.template']
        subs_temp = sub_temp_obj.sudo().browse(int(sub_template_id))
        return {
            subs_temp.id: {
                'presentation_text': subs_temp.presentation_text
                }
            }

    @http.route(['/page/login_subscriber',
                 '/login_subscriber'],
                type='http',
                auth='user',
                website=True)
    def login_subscriber(self, **kwargs):
        return request.redirect('/page/become_subscriber')

    @http.route(['/page/become_subscriber',
                 '/become_subscriber'],
                type='http',
                auth='public',
                website=True)
    def display_subscription_page(self, **kwargs):
        values = self.fill_values(kwargs, load_from_user=True)

        # todo probably duplicate w/ fill_values
        for field in ['email', 'firstname', 'lastname', 'address', 'city',
                      'zip_code', 'country_id', 'error_msg']:
            if kwargs.get(field):
                values[field] = kwargs.pop(field)

        return request.website.render(_BECOME_SUBSCRIBER_TEMPLATE, values)

    def fill_values(self, values, load_from_user=False):
        if values is None:
            values = {}
        sub_temp_obj = request.env['product.subscription.template']
        if load_from_user:
            # the subscriber is connected
            if request.env.user.login != 'public':
                values['logged'] = 'on'
                partner = request.env.user.partner_id
                values['firstname'] = partner.firstname
                values['lastname'] = partner.lastname
                values['email'] = partner.email
                values['street'] = partner.street
                values['zip_code'] = partner.zip
                values['city'] = partner.city
                values['country_id'] = partner.country_id.id
                if partner.parent_id:
                    values['company'] = partner.parent_id.display_name

        if not values.get('product_subscription_id', False):
            values['product_subscription_id'] = 0
        values['subscriptions'] = sub_temp_obj.sudo().search([('publish', '=', True)])
        values['countries'] = self.get_countries()

        if not values.get('country_id'):
            values['country_id'] = '21'

        return values

    def get_countries(self):
        countries = request.env['res.country'].sudo().search([])

        return countries

    def get_address(self, kwargs):
        address = kwargs.get('street', '') + ', ' + kwargs.get('street_number', '')
        vals = {
            'zip': kwargs.get('zip_code'),
            'city': kwargs.get('city'),
            'country_id': kwargs.get('country_id')
        }
        if kwargs.get('box', '').strip() != '':
            address = address + ', ' + kwargs.get('box').strip()
        vals['street'] = address
        return vals

    def check_recaptcha(self, **kwargs):
        if 'g-recaptcha-response' not in kwargs or not request.website.is_captcha_valid(kwargs['g-recaptcha-response']):
            values = self.fill_values({})
            values.update(kwargs)
            values['error_msg'] = _('the captcha has not been validated, '
                                    'please fill in the captcha')

            return request.website.render(_BECOME_SUBSCRIBER_TEMPLATE, values)

    def check_email_confirmation_matches(self, **kwargs):
        is_logged = kwargs.get('logged') == 'on'
        if not is_logged and kwargs.get('email') != kwargs.get('email_confirmation'):
            values = self.fill_values({})
            values.update(kwargs)
            values['error_msg'] = _("email and confirmation email don't match")
            return request.website.render(_BECOME_SUBSCRIBER_TEMPLATE, values)

    def check_email_not_in_database(self, **kwargs):
        is_logged = kwargs.get('logged') == 'on'
        if not is_logged:
            user = request.env['res.users'].sudo().search([('login', '=', kwargs.get('email'))])
            if user:
                values = self.fill_values({})
                values.update(kwargs)
                values['error_msg'] = _('There is an existing account for '
                                        'this mail address. Please login '
                                        'before fill in the form')

                return request.website.render(_BECOME_SUBSCRIBER_TEMPLATE, values)

    def get_subscriber_values(self, **kwargs):
        gift = kwargs.get('gift') == 'on'

        if gift:
            # todo clean variable names
            firstname = kwargs.get('subscriber_firstname').title()
            lastname = kwargs.get('subscriber_lastname').upper()
            email = kwargs.get('subscriber_email')
        else:
            lastname = kwargs.get('lastname').upper()
            firstname = kwargs.get('firstname').title()
            email = kwargs.get('email')

        vals = {
            'name': firstname + ' ' + lastname,
            'lastname': lastname,
            'firstname': firstname,
            'email': email,
            'customer': True,
        }

        vals.update(self.get_address(kwargs))
        return vals

    def get_sponsor_values(self, **kwargs):
        if kwargs.get('gift') == 'on':
            lastname = kwargs.get('lastname').upper()
            firstname = kwargs.get('firstname').title()

            vals = {
                'name': firstname + ' ' + lastname,
                'lastname': lastname,
                'firstname': firstname,
                'email': kwargs.get('email'),
                'customer': True,
            }
            return vals
        else:
            return None

    def get_company_values(self, **kwargs):
        if kwargs.get('gift') == 'on':
            email = kwargs.get('subscriber_email')
        else:
            email = kwargs.get('email')

        vat_number = ''
        if 'vat_number' in kwargs and kwargs.get('vat_number').strip() != '':
            vat_number = kwargs.get('vat_number').strip()

        vals = {
            'name': kwargs.get('company'),
            'email': email,
            'vat': vat_number,
        }
        return vals

    def create_subscription_request(self, **kw):
        vals = {
            'subscriber': kw.get('subscriber_id'),
            'subscription_template': int(kw.get('product_subscription_id')),
            'gift': kw.get('gift') == 'on',
            'sponsor': kw.get('sponsor_id'),
        }
        sub_request = (
            request.env['product.subscription.request']
                   .sudo()
                   .create(vals)
        )
        return sub_request

    def create_user(self, user_values):
        sudo_users = request.env['res.users'].sudo()
        user_id = sudo_users._signup_create_user(user_values)
        sudo_users.with_context({'create_user': True}).action_reset_password()
        return user_id

    def preRenderThanks(self, values, kwargs):
        """ Allow to be overriden """
        return {
            '_values': values,
            '_kwargs': kwargs,
        }

    @http.route(['/render/thanks'],
                type='http',
                auth='public',
                website=True)
    def render_thanks(self, **kw):
        return self.get_subscription_response({}, kw)

    def get_subscription_response(self, values, kw):
        values = self.preRenderThanks(values, kw)
        return request.website.render(_PS_THANKS_TEMPLATE, values)

    def generic_form_checks(self, **kwargs):
        wrong_recaptcha_redirect = self.check_recaptcha(**kwargs)
        if wrong_recaptcha_redirect:
            return wrong_recaptcha_redirect
        email_missmatch_redirect = self.check_email_confirmation_matches(**kwargs)
        if email_missmatch_redirect:
            return email_missmatch_redirect

        email_in_db_redirect = self.check_email_not_in_database(**kwargs)
        if email_in_db_redirect:
            return email_in_db_redirect

    @http.route(['/product_subscription/subscribe'],
                type='http',
                auth='public',
                website=True)
    def product_subscription(self, **kwargs):
        error = self.generic_form_checks(**kwargs)
        if error:
            return error

        subscriber_values = self.get_subscriber_values(**kwargs)
        sponsor_values = self.get_sponsor_values(**kwargs)
        partner_obj = request.env['res.partner']

        if kwargs.get('gift') == 'on':
            if kwargs.get('logged') == 'on':
                subscriber = (
                    partner_obj.sudo().create(subscriber_values)
                )
                sponsor = request.env.user.partner_id
                sponsor.write(sponsor_values)
            else:
                subscriber = (
                    partner_obj.sudo().create(subscriber_values)
                )
                sponsor = partner_obj.sudo().create(sponsor_values)
                self.create_user({
                    'login': sponsor.email,
                    'partner_id': sponsor.id,
                })

            sub_req = self.create_subscription_request(
                subscriber_id=subscriber.id,
                sponsor_id=sponsor.id,
                **kwargs)

        else:
            if kwargs.get('logged') == 'on':
                subscriber = request.env.user.partner_id
                subscriber.write(subscriber_values)
            else:
                subscriber = (
                    partner_obj.sudo().create(subscriber_values)
                )
                self.create_user({
                    'login': subscriber.email,
                    'partner_id': subscriber.id,
                })
            sponsor = subscriber

            sub_req = self.create_subscription_request(
                subscriber_id=subscriber.id,
                sponsor_id=sponsor.id,
                **kwargs)

        if 'company' in kwargs and kwargs.get('company').strip() != '':
            company_values = self.get_company_values(**kwargs)
            partner_obj.sudo().create(company_values)

        values = {
                'subscription_request_id': sub_req,
                'subscriber': sub_req.subscriber.id,
                'subscription_template': sub_req.subscription_template.id,
                'gift': 'on' if sub_req.gift else 'off',
                'sponsor': sub_req.sponsor.id
                if sub_req.sponsor else '',
            }

        return self.get_subscription_response(values, kwargs)
