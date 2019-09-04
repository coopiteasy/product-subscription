# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from utils import add_days, add_months, add_years


class SubscriptionObject(models.Model):
    _name = 'product.subscription.object'
    _order = 'start_date desc'

    name = fields.Char(
        string='Name',
        copy=False)
    subscriber = fields.Many2one(
        comodel_name='res.partner',
        string='Subscriber',
        required=True)
    counter = fields.Float(
        string='Counter')
    subscribed_on = fields.Date(
        string='Subscription date')
    start_date = fields.Date(
        string='Start Date',
        required=True)
    end_date = fields.Date(
        string='End Date',
        compute='_compute_date_end')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('ongoing', 'Ongoing'),
         ('renew', 'Need to Renew'),
         ('terminated', 'Terminated')],
        string='State',
        default='draft')
    request = fields.Many2one(
        comodel_name='product.subscription.request',
        string='Subscription Request')
    template = fields.Many2one(
        comodel_name='product.subscription.template',
        required=True)

    @api.model
    def create(self, vals):
        subscription_sequence = (
            self.env.ref('product_subscription.sequence_product_subscription',
                         False)
         )
        prod_sub_num = subscription_sequence.next_by_id()
        vals['name'] = prod_sub_num

        return super(SubscriptionObject, self).create(vals)

    @api.multi
    @api.depends('start_date', 'template')
    def _compute_date_end(self):
        for subscription in self:
            if not subscription.start_date:
                return False

            elif subscription.template.time_span_unit == 'year':
                subscription.end_date = add_years(
                    subscription.start_date,
                    subscription.template.time_span
                )
            elif subscription.template.time_span_unit == 'month':
                subscription.end_date = add_months(
                    subscription.start_date,
                    subscription.template.time_span
                )
            elif subscription.template.time_span_unit == 'day':
                subscription.end_date = add_days(
                    subscription.start_date,
                    subscription.template.time_span
                )
            else:
                raise ValidationError(_('Timespan unit is not set on template'))

    # todo use write for batch processing
    # @api.multi
    # @api.depends('counter')
    # def _compute_state(self):
    #     for subscription in self:
    #         if not subscription.counter:
    #             subscription.state = 'draft'
    #         elif subscription.counter == 0:
    #             subscription.state = 'terminated'
    #         elif subscription.counter == 1:
    #             subscription.state = 'renew'
    #         else:
    #             subscription.state = 'ongoing'
