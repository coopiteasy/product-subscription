# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, tools
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta  # noqa
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DTF
import logging

_logger = logging.getLogger(__name__
                            )

# operations available for python expression
def pd(dt):
    """parse datetime"""
    return datetime.strptime(dt, DTF) if dt else dt


def fd(dt):
    """format date"""
    return dt.strftime(DTF)


def today_str():
    return fields.Date.today()


def today():
    return pd(fields.Date.today())


class MailingCriterium(models.Model):
    _name = 'ps.mailing.criterium'

    name = fields.Char()
    active = fields.Boolean(
        string='Active',
        default=True)
    template = fields.Many2one(
        comodel_name='product.subscription.template',
        string='Subscription Template',
        required=True)
    mail_template = fields.Many2one(
        comodel_name='mail.template',
        string='Email Template',
        # domain="[('model_id', '=', self.ref('product.subscription.object'))]",
        required=True)
    py_expr_filter = fields.Char(
        string='Python Expression Filter',
        required=False,
        help="Available variables:\n"
             "s: the product subscription object\n"
             "today: date formated as '%Y-%m-%y'\n"
             "datetime, date and timedelta\n"
             "pd(dt): parse string to dates\n"
             "fd(dt): formats date to string")
    nb_subscriptions = fields.Integer(
        string='Subscriptions Reached',
        readonly=True,
        help="Number of subscriptions returned by the filter (click Test "
             "Expression).")
    mail_ids = fields.One2many(
        comodel_name='mail.mail',
        inverse_name='criterium_id',
        string='Scheduled Emails')

    def get_subscriptions(self):
        subscriptions = (
            self.env['product.subscription.object']
                .search([('template', '=', self.template.id)])
        )
        if self.py_expr_filter:
            subscriptions = subscriptions.filtered(
                lambda s: eval(self.py_expr_filter)
            )

        return subscriptions

    @api.multi
    def send_email(self):
        for criterium in self:
            subscriptions = criterium.get_subscriptions()
            _logger.info('Generating %s emails for criterium "%s"' %
                         (len(subscriptions), criterium.name))
            for subscription in subscriptions:
                criterium.mail_template.use_default_to = True
                email_id = criterium.mail_template.send_mail(subscription.id)
                self.env['mail.mail'].browse(email_id).write({
                    'criterium_id': criterium.id,
                    'subscription_id': subscription.id,
                })

    @api.model
    def cron_send_mail(self):
        criteria = self.search([('active', '=', True)])
        criteria.send_email()

    @api.multi
    def test_eval_py_expr_filter(self):
        for criterium in self:
            try:
                subs = criterium.get_subscriptions()
                criterium.nb_subscriptions = len(subs)
            except Exception as e:
                raise ValidationError(e)
