# -*- coding: utf-8 -*-
from openerp import api, models, fields


class SaasClient(models.AbstractModel):
    _name = 'saas_base.client'
    
    users_len = fields.Integer('Count users', readonly=True)
    max_users = fields.Char('Max users allowed', readonly=True)
    file_storage = fields.Integer('File storage (MB)', readonly=True)
    db_storage = fields.Integer('DB storage (MB)', readonly=True)
    expiration_datetime = fields.Datetime('Expiration', track_visibility='onchange')
