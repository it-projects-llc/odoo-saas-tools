# -*- coding: utf-8 -*-
from openerp import models, fields


class OauthApplication(models.Model):
    _inherit = 'oauth.application'

    name = fields.Char('Database name', readonly=True)
    client_id = fields.Char('Client ID', readonly=True, select=True)
    users_len = fields.Integer('Count users', readonly=True)
    file_storage = fields.Integer('File storage (MB)', readonly=True)
    db_storage = fields.Integer('DB storage (MB)', readonly=True)
    server = fields.Char('Server', readonly=True)
