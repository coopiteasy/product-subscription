# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRLfs <http://coopiteasy.be>
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import http
from openerp.exceptions import ValidationError
from openerp.http import request

from subscribe_form import SubscribeForm


class SubscribeController(http.Controller):
    @http.route(
        "/new/subscription/basic", type="http", auth="public", website=True
    )
    def new_subscription_basic(self, **kwargs):
        request.session["redirect_payment"] = kwargs.get("redirect", "")
        self.validate_form()
        if (
            "error" not in request.params
            and request.httprequest.method == "POST"
        ):
            sub_req = self.process_basic_form()
            values = {
                "subscription_request_id": sub_req,
                "subscriber": sub_req.subscriber.id,
                "subscription_template": sub_req.subscription_template.id,
                "gift": "on" if sub_req.gift else "off",
                "sponsor": sub_req.sponsor.id if sub_req.sponsor else "",
            }
            # Template to render thanks
            kwargs[
                "view_callback"
            ] = "website_product_subscription.product_subscription_thanks"
            return self.get_subscription_response(values, kwargs)
        return request.website.render(
            "website_product_subscription.subscribe_form", request.params
        )

    @http.route(
        "/new/subscription/gift", type="http", auth="public", website=True
    )
    def new_subscription_gift(self, **kwargs):
        request.session["redirect_payment"] = kwargs.get("redirect", "")
        self.validate_form()
        if (
            "error" not in request.params
            and request.httprequest.method == "POST"
        ):
            request.params["is_gift"] = True
            sub_req = self.process_gift_form()
            values = {
                "subscription_request_id": sub_req,
                "subscriber": sub_req.subscriber.id,
                "subscription_template": sub_req.subscription_template.id,
                "gift": "on" if sub_req.gift else "off",
                "sponsor": sub_req.sponsor.id if sub_req.sponsor else "",
            }
            # Template to render thanks
            kwargs[
                "view_callback"
            ] = "website_product_subscription.product_subscription_thanks"
            return self.get_subscription_response(values, kwargs)
        return request.website.render(
            "website_product_subscription.subscribe_gift_form", request.params
        )

    @http.route(
        [
            "/new/subscription/generic",
            "/page/login_subscriber",
            "/login_subscriber",
            "/page/become_subscriber",
            "/become_subscriber",
        ],
        type="http",
        auth="public",
        website=True,
    )
    def new_subscription_generic(self, **kwargs):
        request.session["redirect_payment"] = kwargs.get("redirect", "")
        self.validate_form()
        if (
            "error" not in request.params
            and request.httprequest.method == "POST"
        ):
            sub_req = self.process_generic_form()
            values = {
                "subscription_request_id": sub_req,
                "subscriber": sub_req.subscriber.id,
                "subscription_template": sub_req.subscription_template.id,
                "gift": "on" if sub_req.gift else "off",
                "sponsor": sub_req.sponsor.id if sub_req.sponsor else "",
            }
            # Template to render thanks
            kwargs[
                "view_callback"
            ] = "website_product_subscription.product_subscription_thanks"
            return self.get_subscription_response(values, kwargs)
        return request.website.render(
            "website_product_subscription.subscribe_generic_form",
            request.params,
        )

    @http.route(
        ["/subscription/field/presentation_text"],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def get_subscription_presentation_text(self, sub_template_id=None, **kw):
        if sub_template_id is None:
            return {}
        else:
            sub_temp_obj = request.env["product.subscription.template"]
            subs_temp = sub_temp_obj.sudo().browse(int(sub_template_id))
            return {
                subs_temp.id: {
                    "presentation_text": subs_temp.presentation_text
                }
            }

    def validate_form(self):
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

    def process_basic_form(self):
        params = request.params
        self._process_basic_sponsor()
        self._process_basic_subscriber()

        sub_req = self.create_subscription_request()
        params["sub_req_id"] = sub_req.id

        if not request.session.uid:  # already caught by user_exists?
            self._create_web_access(params["login"], params["sponsor_id"])

        return sub_req

    def process_gift_form(self):
        params = request.params
        self._process_gift_sponsor()
        self._process_gift_subscriber()

        sub_req = self.create_subscription_request()
        params["sub_req_id"] = sub_req.id

        self._create_web_access(
            params["subscriber_login"], params["subscriber_id"]
        )

        return sub_req

    def process_generic_form(self):
        params = request.params
        self._process_generic_sponsor()
        self._process_generic_subscriber()

        sub_req = self.create_subscription_request()
        params["sub_req_id"] = sub_req.id

        if params["is_gift"]:
            login = params["subscriber_login"]
            partner_id = params["subscriber_id"]
        else:
            login = params["login"]
            partner_id = params["sponsor_id"]

        self._create_web_access(login, partner_id)

        return sub_req

    def _process_basic_sponsor(self):
        params = request.params
        if params.get("is_company", False):
            self._process_company_sponsor()
            self._process_invoice_address()
        else:
            self._process_person_sponsor()

    def _process_basic_subscriber(self):
        params = request.params
        params["subscriber_id"] = params["sponsor_id"]

    def _process_gift_sponsor(self):
        params = request.params
        if params.get("is_company", False):
            self._process_company_sponsor()
        else:
            self._process_person_sponsor()

    def _process_gift_subscriber(self):
        params = request.params
        partner_obj = request.env["res.partner"]

        # TODO: Explicitly define each keys for company, sponsor,
        #   subscriber. It will be clearer.
        partner_keys = [
            "firstname",
            "lastname",
            "street",
            "zip",
            "city",
            "country_id",
        ]

        sub_email = params["subscriber_login"]
        subscriber_values = {"company_type": "person", "email": sub_email}
        for key in partner_keys:
            subscriber_values[key] = params["subscriber_" + key]
        subscriber = partner_obj.sudo().search([("email", "=", sub_email)])
        if not subscriber:
            subscriber = partner_obj.sudo().create(subscriber_values)
        params["subscriber_id"] = subscriber.id if subscriber else False

    def _process_generic_sponsor(self):
        params = request.params
        if params["is_gift"]:
            self._process_gift_sponsor()
        else:
            self._process_basic_sponsor()

    def _process_generic_subscriber(self):
        params = request.params
        if params["is_gift"]:
            self._process_gift_subscriber()
        else:
            self._process_basic_subscriber()

    def _process_invoice_address(self):
        params = request.params
        partner_obj = request.env["res.partner"]

        representative = params["sponsor_id"]
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

    def fill_values(self, params, load_from_user=False):
        """Kept for compatibility reason."""
        return params

    def get_subscription_request_values(self):
        params = request.params
        gift = params["is_gift"]
        vals = {
            "subscriber": params.get("subscriber_id"),
            "subscription_template": int(params.get("subscription")),
            "gift": gift,
            "type": "gift" if gift else "basic",
            "sponsor": params.get("sponsor_id"),
        }
        return vals

    def create_subscription_request(self):
        vals = self.get_subscription_request_values()
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

    def _process_company_sponsor(self):
        params = request.params
        partner_obj = request.env["res.partner"]

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
        params["sponsor_id"] = representative.id if representative else False

    def _process_person_sponsor(self):
        params = request.params
        partner_obj = request.env["res.partner"]
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
                    "customer": True,
                }
            )
            sponsor = partner_obj.sudo().create(sponsor_values)
        params["sponsor_id"] = sponsor.id if sponsor else False

    def _create_web_access(self, email, partner_id):
        user_obj = request.env["res.users"]

        if not user_obj.user_exist(email):
            user_obj.create_user({"login": email, "partner_id": partner_id})
