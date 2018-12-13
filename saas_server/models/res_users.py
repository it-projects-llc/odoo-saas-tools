# -*- coding: utf-8 -*-
# Copyright 2018 PlanetaTIC <info@planetatic.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, SUPERUSER_ID
from .. import ADMINUSER_ID


class Users(models.Model):
    _inherit = 'res.users'

    @api.model
    def _saas_server_config_oauth(self):
        oauth_provider = self.env.ref('saas_server.saas_oauth_provider')
        self.browse(ADMINUSER_ID).write({
            'oauth_provider_id': oauth_provider.id,
            'oauth_uid': SUPERUSER_ID})

        dbuuid = self.env['ir.config_parameter'].get_param('database.uuid')
        oauth_provider.write({'client_id': dbuuid})
