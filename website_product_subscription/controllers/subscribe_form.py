# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRLfs <http://coopiteasy.be>
#   Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import tools
from openerp.exceptions import ValidationError
from openerp.http import request
from openerp.tools.translate import _


class SubscribeForm():

    def __init__(self, qcontext, user=None, confirm=False, gift=False):
        # Copy reference. Qcontext will be modified in place.
        self.qcontext = qcontext
        self.user = user
        self.confirm = confirm
        self.captcha_check = True
        self.gift = gift

    def normalize_form_data(self):
        """
        Normalize data encoded by the user.
        """
        # The keyword zip is overwrite in the template by the zip
        # standard class of python. So we converted it into 'zip_code'
        # As this happens only in template, we can continue to use 'zip'
        # in the controller.
        if 'zip_code' in self.qcontext:
            self.qcontext['zip'] = self.qcontext['zip_code']
        if 'inv_zip_code' in self.qcontext:
            self.qcontext['inv_zip'] = self.qcontext['inv_zip_code']
        if 'subscriber_zip_code' in self.qcontext:
            self.qcontext['subscriber_zip'] = (
                self.qcontext['subscriber_zip_code']
            )
        # Strip all str values
        for key, val in self.qcontext.items():
            if isinstance(val, str):
                self.qcontext[key] = val.strip()
        # Set upper and title case for names
        if 'firstname' in self.qcontext:
            self.qcontext['firstname'] = self.qcontext['firstname'].title()
        if 'lastname' in self.qcontext:
            self.qcontext['lastname'] = self.qcontext['lastname'].upper()
        if 'subscriber_firstname' in self.qcontext:
            self.qcontext['subscriber_firstname'] = (
                self.qcontext['subscriber_firstname'].title()
            )
        if 'subscriber_lastname' in self.qcontext:
            self.qcontext['subscriber_lastname'] = (
                self.qcontext['subscriber_lastname'].upper()
            )
        # Convert to int when needed
        if 'country_id' in self.qcontext:
            self.qcontext['country_id'] = int(self.qcontext['country_id'])
        if 'inv_country_id' in self.qcontext:
            self.qcontext['inv_country_id'] = int(
                self.qcontext['inv_country_id']
            )
        if 'subscriber_country_id' in self.qcontext:
            self.qcontext['subscriber_country_id'] = int(
                self.qcontext['subscriber_country_id']
            )

    def validate_form(self):
        """
        Populate qcontext with errors if the values given by the user
        are not correct.
        """
        if self.qcontext.get('login', False):
            # Is email ?
            if not tools.single_email_re.match(
                self.qcontext.get('login', '')
            ):
                self.qcontext['error'] = _(
                    "That does not seem to be an email address."
                )
            # Unique email
            other_users = (
                request.env['res.users']
                .sudo()
                .search([('login', '=', self.qcontext.get('login'))])
            )
            if other_users:
                self.qcontext['error'] = _(
                    "There is an existing account for this mail "
                    "address. Please login before fill in the form"
                )
            if self.confirm:
                if self.qcontext.get('login') != self.qcontext.get(
                        'confirm_login'
                ):
                    self.qcontext['error'] = _(
                        "The email and confirmation email must be the same."
                    )
        if self.qcontext.get('subscriber_login', False):
            # Is email ?
            if not tools.single_email_re.match(
                self.qcontext.get('subscriber_login', '')
            ):
                self.qcontext['error'] = _(
                    "That does not seem to be an email address."
                )
            # Unique email
            other_users = (
                request.env['res.users']
                .sudo()
                .search(
                    [('login', '=', self.qcontext.get('subscriber_login'))]
                )
            )
            if other_users:
                self.qcontext['error'] = _(
                    "There is an existing account for the subscriber email "
                    "address. Please login before fill in the form."
                )
            if self.confirm:
                if self.qcontext.get('subscriber_login') != self.qcontext.get(
                        'subscriber_confirm_login'
                ):
                    self.qcontext['error'] = _(
                        "The subscriber email and confirmation email "
                        "must be the same."
                    )
        # Captcha
        if self.captcha_check:
            if request.website.is_captcha_valid(
                self.qcontext.get('g-recaptcha-response', '')
            ):
                self.qcontext['error'] = _(
                    "The captcha has not been validated, please fill "
                    "in the captcha."
                )

    def init_form_data(self):
        """
        Populate qcontext with generic data needed to render the form.
        See also set_form_defaults to set default value to each fields
        of the form.
        """
        self.qcontext.update({
            'countries': request.env['res.country'].sudo().search([]),
            'subscriptions': (
                request.env['product.subscription.template']
                .sudo()
                .search([('publish', '=', True)])
            ),
        })

    def set_form_defaults(self, force=False):
        """
        Populate qcontext with the default value for the form. If user
        is set the default values are values of the user.
        """
        if self.user:
            # TODO: Correct this part to fill with user value
            user = None
            representative = None
            inv_address = None
            is_company = False
            # Fill user and representative
            if self.user.parent_id and self.user.type == 'representative':
                user = self.user.parent_id
                representative = self.user
                is_company = True
            else:
                user = self.user
            # Fill invoice address
            for partner in user.child_ids:
                if partner.type == 'invoice':
                    inv_address = partner
            if 'is_company' not in self.qcontext or force:
                self.qcontext['is_company'] = is_company
            if is_company:
                if 'company_name' not in self.qcontext or force:
                    self.qcontext['company_name'] = user.name
                if 'country_id' not in self.qcontext or force:
                    self.qcontext['country_id'] = (
                        representative.country_id.id
                        if representative.country_id else 0
                    )
                for key in self.user_fields:
                    if key not in self.qcontext or force:
                        self.qcontext[key] = getattr(representative, key)
                if 'invoice_address' not in self.qcontext or force:
                    self.qcontext['invoice_address'] = bool(inv_address)
                if inv_address:
                    if 'inv_country_id' not in self.qcontext or force:
                        self.qcontext['inv_country_id'] = (
                            inv_address.country_id.id
                            if inv_address.country_id else 0
                        )
                    for key in self.invoice_address_fields:
                        if key not in self.qcontext or force:
                            self.qcontext[key] = getattr(
                                inv_address, key[4:]
                            )
            else:
                if 'country_id' not in self.qcontext or force:
                    self.qcontext['country_id'] = (
                        user.country_id.id if user.country_id else 0
                    )
                for key in self.user_fields:
                    if key not in self.qcontext or force:
                        self.qcontext[key] = getattr(user, key)
                if 'invoice_address' not in self.qcontext or force:
                    self.qcontext['invoice_address'] = False
        else:
            if 'country_id' not in self.qcontext or force:
                self.qcontext['country_id'] = (
                    request.env['res.company']
                    .sudo()
                    ._company_default_get()
                    .country_id.id
                )
            if 'inv_country_id' not in self.qcontext or force:
                self.qcontext['inv_country_id'] = (
                    request.env['res.company']
                    .sudo()
                    ._company_default_get()
                    .country_id.id
                )
            if 'subscriber_country_id' not in self.qcontext or force:
                self.qcontext['inv_country_id'] = (
                    request.env['res.company']
                    .sudo()
                    ._company_default_get()
                    .country_id.id
                )

    @property
    def user_fields(self):
        """
        Return names of the fields of a res_user object that are in the
        form.
        """
        return [
            'firstname',
            'lastname',
            'login',
            'street',
            'zip',
            'city',
            'country_id',
        ]

    @property
    def invoice_address_fields(self):
        """
        Return names of the fields of a res_user object that are in the
        form.
        """
        return [
            'inv_street',
            'inv_zip',
            'inv_city',
            'inv_country_id',
        ]

    @property
    def subscriber_fields(self):
        """
        Return names of the fields of a res_user object that are in the
        form.
        """
        return [
            'subscriber_firstname',
            'subscriber_lastname',
            'subscriber_street',
            'subscriber_zip',
            'subscriber_city',
            'subscriber_country_id',
        ]
