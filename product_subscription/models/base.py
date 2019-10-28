# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    firstname = fields.Char(  # fixme how does it interact with module partner_firstname?
        string="First Name"
    )
    lastname = fields.Char(string="Last Name")
    subscriber = fields.Boolean(
        string="Subscriber", compute="_compute_is_subscriber", store=True
    )
    old_subscriber = fields.Boolean(
        string="Old subscriber", compute="_compute_is_subscriber", store=True
    )
    subscriptions = fields.One2many(
        comodel_name="product.subscription.object",
        inverse_name="subscriber",
        string="Subscription",
    )
    requests = fields.One2many(
        comodel_name="product.subscription.request",
        inverse_name="subscriber",
        string="Requests",
    )

    @api.multi
    @api.depends("subscriptions.state")
    def _compute_is_subscriber(self):
        for partner in self:
            subscriptions = partner.subscriptions.filtered(
                lambda s: s.state not in "draft"
            )
            active = partner.subscriptions.filtered(
                lambda s: s.state in ["ongoing", "renew"]
            )
            if subscriptions and active:
                partner.subscriber = True
                partner.old_subscriber = False
            elif subscriptions and not active:
                partner.subscriber = False
                partner.old_subscriber = True
            else:
                # never subscribed
                partner.subscriber = False
                partner.old_subscriber = False


class ProductTemplate(models.Model):
    _inherit = "product.template"

    subscription = fields.Boolean(string="Subscription")
    product_qty = fields.Integer(  # todo duplicate field?
        string="Product quantity"
    )
