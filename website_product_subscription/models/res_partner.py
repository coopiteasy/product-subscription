# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from openerp import models, api

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def has_web_access(self):
        self.ensure_one()
        return self.env["res.users"].user_exists(self.email)

    @api.multi
    def create_web_access(self):
        for partner in self:
            if not partner.email:
                _logger.error(
                    "partner %s %s does not have an email address; cannot create web access"
                    % (partner.id, partner.name)
                )
                continue
            if not partner.has_web_access():
                self.env["res.users"].create_user(
                    {"login": partner.email, "partner_id": partner.id}
                )
