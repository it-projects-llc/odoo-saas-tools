# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
from openerp import SUPERUSER_ID

class oauth_application(osv.Model):
    _inherit = 'oauth.application'

    _columns = {
        'users_len': fields.integer('Count users', readonly=True),
        'file_storage': fields.integer('File storage (MB)', readonly=True),
        'db_storage': fields.integer('DB storage (MB)', readonly=True),
        'server': fields.char('Server', readonly=True),
    }
