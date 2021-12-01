# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def has_web_access(self):
        self.ensure_one()
        return self.env["res.users"].user_exists(self.email)

    @api.multi
    def create_web_access(self):
        for partner in self:
            if not partner.has_web_access():
                self.env["res.users"].create_user(
                    {"login": partner.email, "partner_id": partner.id}
                )
