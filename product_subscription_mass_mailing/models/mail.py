# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, tools


class Mail(models.Model):
    _inherit = 'mail.mail'

    subscription_id = fields.Many2one(
        comodel_name='product.subscription.object',
        string='Subscription')
    subscription_template_id = fields.Many2one(
        comodel_name='product.subscription.template',
        string='Subscription Template',
        related='subscription_id.template')
    criterium_id = fields.Many2one(
        comodel_name='ps.mailing.criterium',
        string='Criterium')
    mail_template_id = fields.Many2one(
        comodel_name='mail.template',
        string='Email Template',
        related='criterium_id.mail_template')


class MailTemplate(models.Model):
    _inherit = 'mail.template'
