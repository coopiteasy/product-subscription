# -*- coding: utf-8 -*-
from datetime import datetime
from openerp import http
from openerp.http import request

from openerp.addons.website_product_subscription.controllers.subscribe import (
    SubscribeController,
)
from openerp.addons.website_payment.controllers.main import website_payment

_RETURN_SUCCESS = "website_product_subscription_online_payment.payment_success"
_RETURN_CANCEL = "website_product_subscription_online_payment.payment_cancel"
_RETURN_ERROR = "website_product_subscription_online_payment.payment_error"


class SubscribeOnlinePayment(SubscribeController):
    def get_online_payment_types(self):
        pay_acq = request.env["payment.acquirer"]
        published_aquirers = pay_acq.search([("website_published", "=", True)])
        payment_types = []
        for acquirer in published_aquirers:
            payment_types.append([acquirer.provider, acquirer.name.title()])
        return payment_types

    def fill_values(self, values, load_from_user=False):
        values = super(SubscribeOnlinePayment, self).fill_values(
            values, load_from_user
        )
        values["providers"] = self.get_online_payment_types()
        return values

    def get_subscription_response(self, values, kw):
        subscription = values.get("subscription_request_id", False)
        pay_acq_obj = request.env["payment.acquirer"]
        pay_trans_obj = request.env["payment.transaction"]
        acquirer = pay_acq_obj.search([("provider", "=", kw.get("provider"))])
        subscription.validate_request()
        reference = subscription.invoice.number
        currency_id = subscription.invoice.currency_id.id
        amount = subscription.invoice.residual

        if acquirer.payment_type == "online":
            if subscription.subscription_template.split_payment:
                amount = subscription.subscription_template.split_payment_price
            return website_payment().pay(
                reference=reference,
                amount=amount,
                currency_id=currency_id,
                acquirer_id=acquirer.id,
            )
        else:
            tx_id = website_payment().transaction(
                reference=reference,
                amount=amount,
                currency_id=currency_id,
                acquirer_id=acquirer.id,
            )
            values["product_subscription_request_id"] = subscription.id
            pay_trans_obj.sudo().browse(tx_id).write(values)
            if subscription.subscription_template.split_payment:
                now = datetime.now().strftime("%d/%m/%Y")
                subscription.invoice.process_subscription(now)
            subscription.send_invoice(subscription.invoice)
            values = self.preRenderThanks(values, kw)
            return request.website.render(
                kw.get("view_callback", "easy_my_coop.cooperator_thanks"),
                values,
            )

    def get_subscription_request_values(self):
        vals = super(
            SubscribeOnlinePayment, self
        ).get_subscription_request_values()
        vals["origin"] = "website"
        return vals

    @http.route(
        ["/render/online_payment_success"],
        type="http",
        auth="public",
        website=True,
    )
    def render_online_payment_success(self, **kw):
        values = self.preRenderThanks({}, kw)
        return request.website.render(_RETURN_SUCCESS, values)

    @http.route(
        ["/render/online_payment_cancel"],
        type="http",
        auth="public",
        website=True,
    )
    def render_online_payment_cancel(self, **kw):
        values = self.preRenderThanks({}, kw)
        return request.website.render(_RETURN_CANCEL, values)

    @http.route(
        ["/render/online_payment_error"],
        type="http",
        auth="public",
        website=True,
    )
    def render_online_payment_error(self, **kw):
        values = self.preRenderThanks({}, kw)
        return request.website.render(_RETURN_ERROR, values)

    def preRenderThanks(self, values, kw):
        """Fill values for rendering thanks messages."""
        values = super(SubscribeOnlinePayment, self).preRenderThanks(
            values, kw
        )
        values["redirect_payment"] = request.session.get(
            "redirect_payment", ""
        )
        return values


class SubscriptionWebsitePayment(website_payment):
    @http.route(
        ["/website_payment/transaction"],
        type="json",
        auth="public",
        website=True,
    )
    def transaction(self, reference, amount, currency_id, acquirer_id):
        tx_id = super(SubscriptionWebsitePayment, self).transaction(
            reference, amount, currency_id, acquirer_id
        )
        tx = request.env["payment.transaction"].sudo().browse(tx_id)
        inv_obj = request.env["account.invoice"]
        subscription = inv_obj.sudo().search(
            [("subscription", "=", True), ("number", "=", reference)]
        )
        vals = {}
        if len(subscription) > 0:
            vals[
                "product_subscription_request_id"
            ] = subscription.product_subscription_request.id
            tx.sudo().write(vals)

        return tx_id
