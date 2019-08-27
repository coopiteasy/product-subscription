# -*- coding: utf-8 -*-
import requests
import json
from datetime import datetime
import logging

from openerp import api, fields, models

_logger = logging.getLogger(__name__)


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    payment_type = fields.Selection([('online', 'Online'),
                                     ('deferred', 'Deferred')],
                                    string='Payment Type',
                                    default="deferred")


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    payment_type = fields.Selection(related='acquirer_id.payment_type',
                                    readonly=True)
    product_subscription_request_id = fields.Many2one(
                                      'product.subscription.request',
                                      string="Product subscription"
                                      " request",
                                      readonly=True)

    @api.model
    def process_prod_sub_online_payment_reception(self, tx):
        if tx.product_subscription_request_id:
            prod_sub_request = tx.product_subscription_request_id
            prod_sub_request.state = 'paid'
            effective_date = datetime.now().strftime("%d/%m/%Y")
            prod_sub_request.sudo().invoice.process_subscription(effective_date)

        return True

    # TODO does this should go in a dedicated module?
    @api.model
    def _mollie_form_validate(self, tx, data):
        reference = data.get('reference')

        acquirer = tx.acquirer_id

        transactionId = tx['acquirer_reference']

        _logger.info('Validated transfer payment for tx %s: set as '
                     'pending' % (reference))
        mollie_api_key = acquirer._get_mollie_api_keys(acquirer.environment)['mollie_api_key']
        url = "%s/payments" % (acquirer._get_mollie_urls(acquirer.environment)['mollie_form_url'])

        payload = {
            "id": transactionId
        }
        if acquirer.environment == 'test':
            payload["testmode"] = True

        headers = {'content-type': 'application/json',
                   'Authorization': 'Bearer ' + mollie_api_key}

        mollie_response = requests.get(
            url, data=json.dumps(payload), headers=headers).json()

        if self.state == 'done':
            _logger.info('Mollie: trying to validate an already '
                         'validated tx (ref %s)', reference)
            return True

        data_list = mollie_response["data"]
        data = {}
        status = 'undefined'
        mollie_reference = ''
        if len(data_list) > 0:
            data = data_list[0]

        if "status" in data:
            status = data["status"]
        if "id" in data:
            mollie_reference = data["id"]

        if status == "paid":
            vals = {
                'state': 'done',
                'date_validate':  fields.datetime.strptime(data["paidDatetime"].replace(".0Z", ""), "%Y-%m-%dT%H:%M:%S"),
                'acquirer_reference': mollie_reference,
            }

            tx.write(vals)
            if tx.callback_eval:
                safe_eval(tx.callback_eval, {'self': tx})

            self.process_prod_sub_online_payment_reception(tx)
            return True
        elif status in ["cancelled", "expired", "failed"]:
            tx.write({
                'state': 'cancel',
                'acquirer_reference': mollie_reference,
            })
            return False
        elif status in ["open", "pending"]:
            tx.write({
                'state': 'pending',
                'acquirer_reference': mollie_reference,
            })
            return False
        else:
            tx.write({
                'state': 'error',
                'acquirer_reference': mollie_reference,
            })
            return False
