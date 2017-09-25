# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, values):
        # overridden to signup along with creation of db through saas backend wizard
        user = super(ResUsers, self).create(values)
        if self.env.context.get('saas_signup'):
            user.partner_id.signup_prepare()
        return user
