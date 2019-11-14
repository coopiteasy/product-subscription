# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRLfs <http://coopiteasy.be>
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import http
from openerp.exceptions import ValidationError
from openerp.http import request
from openerp.tools.translate import _

from openerp.addons.website_product_subscription.controllers.subscribe_form import (
    SubscribeForm,
)


class SubscribeController(http.Controller):
    @http.route(
        "/new/subscription/basic", type="http", auth="public", website=True
    )
    def new_subscription_basic(self, **kwargs):
        request.session["redirect_payment"] = kwargs.get("redirect", "")
        self.new_subscription_basic_form_validation()
        if (
            "error" not in request.params
            and request.httprequest.method == "POST"
        ):
            sub_req = self.process_new_subscription_basic_form()
            values = {
                "subscription_request_id": sub_req,
                "subscriber": sub_req.subscriber.id,
                "subscription_template": sub_req.subscription_template.id,
                "gift": "off",
                "sponsor": sub_req.sponsor.id if sub_req.sponsor else "",
            }
            # Template to render thanks
            kwargs[
                "view_callback"
            ] = "website_product_subscription.product_subscription_thanks"
            return self.get_subscription_response(values, kwargs)
        return request.website.render(
            "website_product_subscription.new_subscription_basic", request.params
        )

    @http.route(
        "/new/subscription/gift", type="http", auth="public", website=True
    )
    def new_subscription_gift(self, **kwargs):
        request.session["redirect_payment"] = kwargs.get("redirect", "")
        self.new_subscription_gift_form_validation()
        if (
            "error" not in request.params
            and request.httprequest.method == "POST"
        ):
            sub_req = self.process_new_subscription_gift_form()
            values = {
                "subscription_request_id": sub_req,
                "subscriber": sub_req.subscriber.id,
                "subscription_template": sub_req.subscription_template.id,
                "gift": "on",
                "sponsor": sub_req.sponsor.id if sub_req.sponsor else "",
            }
            # Template to render thanks
            kwargs[
                "view_callback"
            ] = "website_product_subscription.product_subscription_thanks"
            return self.get_subscription_response(values, kwargs)
        return request.website.render(
            "website_product_subscription.new_subscription_gift", request.params
        )

    def new_subscription_basic_form_validation(self):
        """Execute form check and validation"""
        user = None
        if request.session.uid:
            user = request.env["res.users"].browse(request.session.uid)
        form = SubscribeForm(request.params, user, confirm=(not user))
        form.normalize_form_data()
        form.validate_form()
        form.init_form_data()
        self.fill_values(request.params)
        if request.httprequest.method == "GET" or "error" in request.params:
            form.set_form_defaults()

    def new_subscription_gift_form_validation(self):
        """Execute form check and validation"""
        user = None
        if request.session.uid:
            user = request.env["res.users"].browse(request.session.uid)
        form = SubscribeForm(request.params, user, confirm=(not user))
        form.normalize_form_data()
        form.validate_form()
        form.init_form_data()
        self.fill_values(request.params)
        if request.httprequest.method == "GET":  # fixme? `or error in request.params`
            form.set_form_defaults()

    def process_new_subscription_basic_form(self):
        params = request.params
        partner_obj = request.env["res.partner"]
        user_obj = request.env["res.users"]
        # Sponsor
        if params.get("is_company", False):
            # Company
            company_values = {
                "street": params["street"],
                "zip": params["zip"],
                "city": params["city"],
                "country_id": params["country_id"],
            }
            if request.session.uid:
                company = request.env.user.parent_id
                company.write(company_values)
            else:
                company_values.update(
                    {
                        "customer": True,
                        "company_type": "company",
                        "name": params["company_name"],
                        "email": params["login"],
                    }
                )
                company = partner_obj.sudo().create(company_values)
            params["company_id"] = company.id if company else False
            # Representative
            repr_values = {
                "street": params["street"],
                "zip": params["zip"],
                "city": params["city"],
                "country_id": params["country_id"],
            }
            if request.session.uid:
                representative = request.env.user.partner_id
                representative.write(repr_values)
            else:
                repr_values.update(
                    {
                        "type": "representative",
                        "customer": True,
                        "company_type": "person",
                        "parent_id": company.id,
                        "email": params["login"],
                        "login": params["login"],
                        "firstname": params["firstname"],
                        "lastname": params["lastname"],
                    }
                )
                representative = partner_obj.sudo().create(repr_values)
            try:
                representative.vat = params["vat"]
            except ValidationError as err:
                request.params["error"] = err.name
            params["representative_id"] = (
                representative.id if representative else False
            )
            params["sponsor_id"] = (
                representative.id if representative else False
            )
            # Invoice address
            inv_add_values = {
                "parent_id": representative.id,
                "type": "invoice",
                "street": params["inv_street"],
                "city": params["inv_city"],
                "zip": params["inv_zip"],
                "country_id": params["inv_country_id"],
            }
            if request.session.uid:
                invoice_address = None
                for address in request.env.user.child_ids:
                    if address.type == "invoice":
                        invoice_address = address
                if invoice_address:
                    invoice_address.write(inv_add_values)
            else:
                invoice_address = partner_obj.sudo().create(inv_add_values)
            params["invoice_address_id"] = (
                invoice_address.id if invoice_address else False
            )
        else:
            sponsor_values = {
                "street": params["street"],
                "zip": params["zip"],
                "city": params["city"],
                "country_id": params["country_id"],
            }
            if request.session.uid:
                sponsor = request.env.user.partner_id
                sponsor.write(sponsor_values)
            else:
                sponsor_values.update(
                    {
                        "name": params["firstname"] + " " + params["lastname"],
                        "firstname": params["firstname"],
                        "lastname": params["lastname"],
                        "email": params["login"],
                        "login": params["login"],
                        "customer": True,
                    }
                )
                sponsor = partner_obj.sudo().create(sponsor_values)
            params["sponsor_id"] = sponsor.id if sponsor else False

        params["subscriber_id"] = params["sponsor_id"]

        sub_req = self.create_subscription_request(params, gift=False)
        params["sub_req_id"] = sub_req.id

        if not request.session.uid:
            # Create webaccess
            if not user_obj.user_exist(params["login"]):
                user_obj.create_user(
                    {
                        "login": params["login"],
                        "partner_id": params["sponsor_id"],
                    }
                )
        return sub_req

    def process_new_subscription_gift_form(self):
        params = request.params
        partner_obj = request.env["res.partner"]
        user_obj = request.env["res.users"]
        # TODO: Explicitly define each keys for company, sponsor,
        # subscriber. It will be clearer.
        partner_keys = [
            "firstname",
            "lastname",
            "login",
            "street",
            "zip",
            "city",
            "country_id",
        ]
        # Sponsor
        if params.get("is_company", False):
            # Company
            company_values = {
                "street": params["street"],
                "zip": params["zip"],
                "city": params["city"],
                "country_id": params["country_id"],
            }
            if request.session.uid:
                company = request.env.user.parent_id
                company.write(company_values)
            else:
                company_values.update(
                    {
                        "customer": True,
                        "company_type": "company",
                        "name": params["company_name"],
                        "email": params["login"],
                    }
                )
                company = partner_obj.sudo().create(company_values)
            params["company_id"] = company.id if company else False
            # Representative
            repr_values = {
                "street": params["street"],
                "zip": params["zip"],
                "city": params["city"],
                "country_id": params["country_id"],
            }
            if request.session.uid:
                representative = request.env.user.partner_id
                representative.write(repr_values)
            else:
                repr_values.update(
                    {
                        "type": "representative",
                        "customer": True,
                        "company_type": "person",
                        "parent_id": company.id,
                        "email": params["login"],
                        "login": params["login"],
                        "firstname": params["firstname"],
                        "lastname": params["lastname"],
                    }
                )
                representative = partner_obj.sudo().create(repr_values)
            try:
                representative.vat = params["vat"]
            except ValidationError as err:
                request.params["error"] = err.name
            params["representative_id"] = (
                representative.id if representative else False
            )
            params["sponsor_id"] = (
                representative.id if representative else False
            )
        else:
            if request.session.uid:
                sponsor = request.env.user.partner_id
            else:
                sponsor_values = {
                    "name": params["firstname"] + " " + params["lastname"],
                    "email": params["login"],
                    "customer": True,
                }
                for key in partner_keys:
                    sponsor_values[key] = params.get(key, False)
                sponsor = partner_obj.sudo().search(
                    [("email", "=", sponsor_values.get("email"))]
                )
                if not sponsor:
                    sponsor = partner_obj.sudo().create(sponsor_values)
            params["sponsor_id"] = sponsor.id if sponsor else False

        # Subscriber
        sub_email = params["subscriber_login"]
        subscriber_values = {"company_type": "person", "email": sub_email}
        for key in partner_keys:
            subscriber_values[key] = params["subscriber_" + key]
        subscriber = partner_obj.sudo().search([("email", "=", sub_email)])
        if not subscriber:
            subscriber = partner_obj.sudo().create(subscriber_values)
        params["subscriber_id"] = subscriber.id if subscriber else False

        sub_req = self.create_subscription_request(params, gift=True)
        params["sub_req_id"] = sub_req.id

        # Create webaccess
        if not user_obj.user_exist(sub_email):
            user_obj.create_user(
                {
                    "login": params["subscriber_login"],
                    "partner_id": params["subscriber_id"],
                }
            )
        return sub_req

    def fill_values(self, params, load_from_user=False):
        """Kept for compatibility reason."""
        return params

    def get_subscription_request_values(self, params, gift):
        vals = {
            "subscriber": params.get("subscriber_id"),
            "subscription_template": int(params.get("subscription")),
            "gift": gift,
            "type": "gift" if gift else "basic",
            "sponsor": params.get("sponsor_id"),
        }
        return vals

    def create_subscription_request(self, params, gift):
        vals = self.get_subscription_request_values(params, gift)
        sub_request = (
            request.env["product.subscription.request"].sudo().create(vals)
        )
        return sub_request

    def get_subscription_response(self, values, kw):
        values = self.preRenderThanks(values, kw)
        return request.website.render(
            "website_product_subscription.product_subscription_thanks", values
        )

    def preRenderThanks(self, values, kwargs):
        """
        Use this function to fill context givent to render of the
        thanks response.
        """
        return {
            "_values": values,
            "_kwargs": kwargs,
            # Give redirect object to success page
            "redirect_payment": request.session.get("redirect_payment", ""),
        }
