# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, tools


class ProductSubscriptionObject(models.Model):
    _inherit = "product.subscription.object"

    mail_ids = fields.One2many(
        comodel_name="mail.mail",
        inverse_name="subscription_id",
        string="Scheduled Emails",
    )
    email_to = fields.Char(string="Email To", related="subscriber.email")

    @api.multi
    def message_get_default_recipients(self):
        return {
            s.id: {
                "partner_ids": [s.subscriber.id],
                "email_to": s.subscriber.email,
                "email_cc": False,
            }
            for s in self
        }
