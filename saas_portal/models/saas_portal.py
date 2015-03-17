# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields
from openerp.addons.saas_utils import connector, database
from openerp import http
from contextlib import closing


class OauthApplication(models.Model):
    _inherit = 'oauth.application'

    name = fields.Char('Database name', readonly=True)
    client_id = fields.Char('Client ID', readonly=True, select=True)
    users_len = fields.Integer('Count users', readonly=True)
    file_storage = fields.Integer('File storage (MB)', readonly=True)
    db_storage = fields.Integer('DB storage (MB)', readonly=True)
    server = fields.Char('Server', readonly=True)

    def edit_db(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'saas.config',
            'target': 'new',
            'context': {
                'default_action': 'edit',
                'default_database': obj.name
            }
        }

    def upgrade_db(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'saas.config',
            'target': 'new',
            'context': {
                'default_action': 'upgrade',
                'default_database': obj.name
            }
        }


class SaasConfig(models.TransientModel):
    _name = 'saas.config'

    action = fields.Selection([('edit', 'Edit'), ('upgrade', 'Upgrade')],
                                'Action')
    database = fields.Char('Database', size=128)
    addons = fields.Char('Addons', size=256)

    def execute_action(self, cr, uid, ids, context=None):
        res = False
        obj = self.browse(cr, uid, ids[0], context)
        method = '%s_database' % obj.action
        if hasattr(self, method):
            res = getattr(self, method)(cr, uid, obj, context)
        return res

    def edit_database(self, cr, uid, obj, context=None):
        params = (obj.database.replace('_', '.'), obj.database)
        url = 'http://%s/login?db=%s&login=admin&key=admin' % params
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'name': 'Edit Database',
            'url': url
        }

    def upgrade_database(self, cr, uid, obj, context=None):
        dbs = []
        if obj.databse:
            dbs = [obj.database]
        else:
            dbs = database.get_market_dbs()
        domain = [('name', 'in', obj.addons.split(','))]
        for db_name in dbs:
            openerp.sql_db.close_db(db_name)
            db = openerp.sql_db.db_connect('postgres')
            with closing(db.cursor()) as cr:
                cr.autocommit(True)     # avoid transaction block
                openerp.service.db._drop_conn(cr, db_name)
                aids = connector.call(db_name, 'ir.module.module', 'search', domain)
                connector.call(db_name, 'ir.module.module', 'button_upgrade', aids)
        return True
