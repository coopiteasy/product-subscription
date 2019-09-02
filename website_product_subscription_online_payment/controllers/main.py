# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request

from openerp.addons.website_product_subscription.controllers.main import WebsiteProductSubscription
from openerp.addons.website_payment.controllers.main import website_payment

_RETURN_SUCCESS = "website_product_subscription_online_payment.payment_success"
_RETURN_CANCEL = "website_product_subscription_online_payment.payment_cancel"
_RETURN_ERROR = "website_product_subscription_online_payment.payment_error"


class ProductSubscriptionOnlinePayment(WebsiteProductSubscription):

    @http.route(['/render/online_payment_succes'],
                type='http',
                auth='public',
                website=True)
    def render_online_payment_success(self, **kw):
        values = self.preRenderThanks({}, kw)
        return request.website.render(_RETURN_SUCCESS, values)

    @http.route(['/render/online_payment_cancel'],
                type='http',
                auth='public',
                website=True)
    def render_online_payment_cancel(self, **kw):
        values = self.preRenderThanks({}, kw)
        return request.website.render(_RETURN_CANCEL, values)

    @http.route(['/render/online_payment_error'],
                type='http',
                auth='public',
                website=True)
    def render_online_payment_error(self, **kw):
        values = self.preRenderThanks({}, kw)
        return request.website.render(_RETURN_ERROR, values)

    def get_online_payment_types(self):
        pay_acq = request.env['payment.acquirer']
        published_aquirers = pay_acq.search([('website_published', '=', True)])
        payment_types = []
        for acquirer in published_aquirers:
            payment_types.append([acquirer.provider,
                                 acquirer.provider.title()])
        return payment_types

    def fill_values(self, values, load_from_user=False):
        values = super(ProductSubscriptionOnlinePayment, self).fill_values(values, load_from_user)
        values['providers'] = self.get_online_payment_types()

        return values

    def get_subscription_response(self, values, kw):
        subscription = values.get('subscription_request_id', False)
        pay_acq_obj = request.env['payment.acquirer']
        acquirer = pay_acq_obj.search([('provider', '=', kw.get('provider'))])
        if acquirer.payment_type == 'online':
            subscription.validate_request()
            return website_payment().pay(reference=subscription.invoice.number,
                                         amount=subscription.invoice.residual,
                                         currency_id=subscription.invoice.currency_id.id,
                                         acquirer_id=acquirer.id)
        else:
            values = self.preRenderThanks(values, kw)
            return request.website.render(kw.get(
                                            "view_callback",
                                            "easy_my_coop.cooperator_thanks"),
                                          values)

        return True


class SubscriptionWebsitePayment(website_payment):

    @http.route(['/website_payment/transaction'],
                type='json',
                auth="public", website=True)
    def transaction(self, reference, amount, currency_id, acquirer_id):
        tx_id = super(SubscriptionWebsitePayment, self).transaction(
                                                                reference,
                                                                amount,
                                                                currency_id,
                                                                acquirer_id)
        tx = request.env['payment.transaction'].sudo().browse(tx_id)
        inv_obj = request.env['account.invoice']
        subscription = inv_obj.sudo().search([('subscription', '=', True),
                                              ('number', '=', reference)])
        vals = {}
        if len(subscription) > 0:
            vals['product_subscription_request_id'] = subscription.product_subscription_request.id
            tx.sudo().write(vals)

        return tx_id
