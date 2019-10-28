# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class Website(models.Model):
    _inherit = "website"

    temporary_access_length = fields.Integer(
        string="Temporary Access (days)",
        default=30,
        required=True,
        help="Sets how many days the user can access the website before "
        "paying the invoice.",
    )


class WebsiteConfigSettings(models.Model):
    _inherit = "website.config.settings"

    temporary_access_length = fields.Integer(
        related="website_id.temporary_access_length"
    )
