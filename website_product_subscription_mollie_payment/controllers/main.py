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
        pay_tx_obj = request.env['payment.transaction']
        pay_tx_obj.sudo().form_feedback(post, 'mollie')
        orderid = post['reference']
        tx = pay_tx_obj.sudo().search([('reference', '=', orderid)])
        if tx and tx.product_subscription_request_id:
            return werkzeug.utils.redirect("/render/thanks")
        return werkzeug.utils.redirect("/shop/payment/validate")
