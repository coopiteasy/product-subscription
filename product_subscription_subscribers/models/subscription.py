# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class SubscriptionRequest(models.Model):
    _inherit = "product.subscription.request"

    additional_subscribers = fields.Many2many(
        comodel_name="res.partner", string="Additional Subscribers"
    )
    subscriber = fields.Many2one(string="Main Subscriber")


class SubscriptionObject(models.Model):
    _inherit = "product.subscription.object"

    additional_subscribers = fields.Many2many(
        comodel_name="res.partner", string="Additional Subscribers"
    )
    subscriber = fields.Many2one(string="Main Subscriber")
