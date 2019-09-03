# -*- coding: utf-8 -*-
import logging
import werkzeug

from openerp import http
from openerp.http import request
from openerp.addons.payment_mollie_official.controllers.main import MollieController

_logger = logging.getLogger(__name__)


class ProductSubscriptionMollieController(MollieController):

    @http.route([
        '/payment/mollie/redirect'], type='http', auth="none", methods=['GET'])
    def mollie_redirect(self, **post):
        route = '/shop/payment/validate'
        pay_tx_obj = request.env['payment.transaction']
        pay_tx_obj.sudo().form_feedback(post, 'mollie')
        orderid = post['reference']
        tx = pay_tx_obj.sudo().search([('reference', '=', orderid)])
        if tx and tx.product_subscription_request_id:
            if tx.state == 'done':
                route = '/render/online_payment_success'
            elif tx.state == 'cancel':
                route = '/render/online_payment_cancel'
            elif tx.state == 'error':
                route = '/render/online_payment_error'
        return werkzeug.utils.redirect(route)
