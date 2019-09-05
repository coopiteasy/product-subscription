# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api, _


class SubscriptionTemplate(models.Model):
    _name = 'product.subscription.template'

    name = fields.Char(
        string='Subscription name',
        copy=False,
        required=True)
    description = fields.Char(
        string='Description')
    product_qty = fields.Integer(  # todo duplicate field?
        string='Subscription quantity',
        required=True,
        help='This is the quantity of product that'
             ' will be allocated by this subscription')
    time_span = fields.Integer(
        string='Time Span',
        default=1,
        required=True)
    time_span_unit = fields.Selection(
        string='Time Span Unit',
        selection=[('year', 'Year'),
                   ('month', 'Month'),
                   ('day', 'Day')],
        default='year',
        required=True)
    price = fields.Float(
        related='product.lst_price',
        string='Subscription price',
        readonly=True)
    publish = fields.Boolean(
        string='Publish on website')
    product = fields.Many2one(
        comodel_name='product.template',
        string='Product',
        domain=[('subscription', '=', True)],
        required=True)
    released_products = fields.Many2many(
        comodel_name='product.template',
        string='Released Product')
    analytic_distribution = fields.Many2one(
        comodel_name='account.analytic.distribution',
        string='Analytic distribution')
    journal = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        required=True,
        domain=[('type', '=', 'sale')])

