# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRLfs <http://coopiteasy.be>
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Rémy Taymans <remy@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import http
from openerp.http import request
from openerp.fields import Date
from subscribe_form import SubscribeForm

import logging

_logger = logging.getLogger(__name__)


class SubscribeController(http.Controller):
    @http.route(
        "/new/subscription/basic", type="http", auth="public", website=True
    )
    def new_subscription_basic(self, **kwargs):
        request.params["form_type"] = "basic"
        template = "website_product_subscription.subscribe_form"
        return self.new_subscription(template, **kwargs)

    @http.route(
        "/new/subscription/gift", type="http", auth="public", website=True
    )
    def new_subscription_gift(self, **kwargs):
        request.params["form_type"] = "gift"
        template = "website_product_subscription.subscribe_gift_form"
        return self.new_subscription(template, **kwargs)

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
        request.params["form_type"] = "generic"
        template = "website_product_subscription.subscribe_generic_form"
        return self.new_subscription(template, **kwargs)

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

    def new_subscription(self, template, **kwargs):
        request.session["redirect_payment"] = kwargs.get("redirect", "")
        self.validate_form()
        if (
            "error" not in request.params
            and request.httprequest.method == "POST"
        ):
            sub_req = self.process_form()
            gift_subscriber_exists = request.params.get(
                "gift_subscriber_exists", False
            )
            values = {
                "subscription_request_id": sub_req,
                "subscriber": sub_req.subscriber.id,
                "subscription_template": sub_req.subscription_template.id,
                "gift": "on" if sub_req.gift else "off",
                "sponsor": sub_req.sponsor.id if sub_req.sponsor else "",
                "gift_subscriber_exists": gift_subscriber_exists,
            }
            # Template to render thanks
            kwargs[
                "view_callback"
            ] = "website_product_subscription.product_subscription_thanks"
            return self.get_subscription_response(values, kwargs)
        return request.website.render(template, request.params)

    def process_form(self):
        params = request.params
        self._process_sponsor()
        self._process_subscriber()

        sub_req = self.create_subscription_request()
        sub_req.create_web_access()

        params["sub_req_id"] = sub_req.id
        return sub_req

    def _process_sponsor(self):
        params = request.params
        if params.get("is_company", False):
            self._process_company_sponsor()
        else:
            self._create_sponsor()

    def _process_subscriber(self):
        params = request.params

        if params["is_gift"]:
            partner_obj = request.env["res.partner"]

            subscriber_email = params["subscriber_login"]
            subscriber_values = {
                "company_type": "person",
                "firstname": params["subscriber_firstname"],
                "lastname": params["subscriber_lastname"],
                "street": params["subscriber_street"],
                "zip": params["subscriber_zip"],
                "city": params["subscriber_city"],
                "country_id": params["subscriber_country_id"],
            }

            subscriber = partner_obj.sudo().search(
                [("email", "=", subscriber_email)]
            )
            if not subscriber:
                subscriber_values["email"] = subscriber_email
                subscriber = partner_obj.sudo().create(subscriber_values)

            params["subscriber_id"] = subscriber.id if subscriber else False
        else:
            params["subscriber_id"] = params["sponsor_id"]

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

    def fill_values(self, params, load_from_user=False):
        """Kept for compatibility reason."""
        return params

    def get_subscription_request_values(self):
        params = request.params
        gift = params["is_gift"]

        if gift:
            gift_date = params.get("gift_date", Date.today())
        else:
            gift_date = False

        vals = {
            "subscriber": params.get("subscriber_id"),
            "subscription_template": int(params.get("subscription")),
            "gift": gift,
            "gift_date": gift_date,
            "type": "gift" if gift else "basic",
            "sponsor": params.get("sponsor_id"),
        }
        return vals

    def create_subscription_request(self):
        vals = self.get_subscription_request_values()
        sub_request = (
            request.env["product.subscription.request"].sudo().create(vals)
        )
        _logger.debug(
            "Created  subscription request w/ date %s"
            % sub_request.subscription_date
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

    def _create_sponsor(self, company=None):
        params = request.params
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
                    "firstname": params["firstname"],
                    "lastname": params["lastname"],
                    # "name": params["firstname"] + " " + params["lastname"],
                    "customer": True,
                    "email": params["login"],
                }
            )

            if company:
                sponsor_values.update(
                    {
                        "type": "representative",
                        "company_type": "person",
                        "parent_id": company.id,
                    }
                )

            sponsor = request.env["res.partner"].sudo().create(sponsor_values)

        params["sponsor_id"] = sponsor.id if sponsor else False
        return sponsor

    def _process_company_sponsor(self):
        company = self._process_company_sponsor_company()
        self._create_sponsor(company)
        self._create_invoice_address(company)

    def _process_company_sponsor_company(self):
        params = request.params

        shipping_address = {
            "street": params["street"],
            "zip": params["zip"],
            "city": params["city"],
            "country_id": params["country_id"],
            "vat": params["vat"],
        }

        # create/update company
        if request.session.uid and request.env.user.parent_id:
            company = request.env.user.parent_id
            company.write(shipping_address)
        elif request.session.uid and not request.env.user.parent_id:
            shipping_address.update(
                {
                    "customer": True,
                    "company_type": "company",
                    "name": params["company_name"],
                    "email": params["login"],
                }
            )
            company = (
                request.env["res.partner"].sudo().create(shipping_address)
            )
            request.env.user.parent_id = company
        else:
            shipping_address.update(
                {
                    "customer": True,
                    "company_type": "company",
                    "name": params["company_name"],
                    "email": params["login"],
                }
            )
            company = (
                request.env["res.partner"].sudo().create(shipping_address)
            )

        params["company_id"] = company.id if company else False
        return company

    def _create_invoice_address(self, company):
        params = request.params
        if params.get("invoice_address", False):
            invoice_address = {
                "parent_id": company.id,
                "type": "invoice",
                "street": params["inv_street"],
                "zip": params["inv_zip"],
                "city": params["inv_city"],
                "country_id": params["inv_country_id"],
                "vat": params["vat"],
            }
            invoice_partners = company.child_ids.filtered(
                lambda p: p.type == "invoice"
            )
            if invoice_partners:
                invoice_partner = invoice_partners[0]
                invoice_partner.write(invoice_address)
            else:
                request.env["res.partner"].sudo().create(invoice_address)
