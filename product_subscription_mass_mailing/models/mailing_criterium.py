# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, tools
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta  # noqa
today = fields.Date.today()


class MailingCriterium(models.Model):
    _name = 'ps.mailing.criterium'

    name = fields.Char()
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
             "datetime, date and timedelta")
    nb_subscriptions = fields.Integer(
        string='Subscriptions returned by criterium',
        compute='test_eval_py_expr_filter')
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
            for subscription in subscriptions:
                criterium.mail_template.use_default_to = True
                email_id = criterium.mail_template.send_mail(subscription.id)
                self.env['mail.mail'].browse(email_id).write({
                    'criterium_id': criterium.id,
                    'subscription_id': subscription.id,
                })

    @api.multi
    @api.depends('py_expr_filter')
    def test_eval_py_expr_filter(self):
        for criterium in self:
            try:
                subs = criterium.get_subscriptions()
                criterium.nb_subscriptions = len(subs)
            except Exception as e:
                raise ValidationError(e)
