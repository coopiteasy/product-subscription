# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine BAKKALI <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import models


class ResUsers(models.Model):
    _inherit = "res.users"

    def create_user(self, user_values):
        sudo_users = self.env["res.users"].sudo()
        user_id = sudo_users._signup_create_user(user_values)
        user = sudo_users.browse(user_id)
        user.with_context({"create_user": True}).action_reset_password()
        return user_id

    def user_exists(self, login):
        sudo_users = self.env["res.users"].sudo()
        user = sudo_users.search([("login", "=", login)])
        if user:
            return True
        else:
            return False
