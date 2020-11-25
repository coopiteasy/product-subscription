# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def create_web_access(self):
        User = self.env["res.users"]
        for partner in self:
            if not User.user_exists(partner.email):
                User.create_user(
                    {"login": partner.email, "partner_id": partner.id}
                )
