# -*- coding: utf-8 -*-
from odoo import models


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _auth_oauth_validate(self, provider, access_token):
        validation = super(ResUsers, self)._auth_oauth_validate(provider, access_token)
        client_id = validation.get('client_id')
        if client_id:
            p = self.env['auth.oauth.provider'].browse(provider)
            assert client_id == p.client_id, "wrong client_id"
        return validation
