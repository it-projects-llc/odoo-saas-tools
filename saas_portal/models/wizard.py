# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api, SUPERUSER_ID
from openerp.addons.saas_utils import connector, database
from openerp import http


class SaasConfig(models.TransientModel):
    _name = 'saas.config'

    action = fields.Selection([('edit', 'Edit'), ('upgrade', 'Upgrade'), ('delete', 'Delete')],
                                'Action')
    database = fields.Char('Database', size=128)
    server_id = fields.Many2one('saas_portal.server', string='Server')
    update_addons = fields.Char('Update Addons', size=256)
    install_addons = fields.Char('Install Addons', size=256)
    fix_ids = fields.One2many('saas.config.fix', 'config_id', 'Fixes')
    description = fields.Text('Description')

    def execute_action(self, cr, uid, ids, context=None):
        res = False
        obj = self.browse(cr, uid, ids[0], context)
        method = '%s_database' % obj.action
        if hasattr(self, method):
            res = getattr(self, method)(cr, uid, obj, context)
        return res

    @api.one
    def delete_database(self):
        state = {
            'd': self.database
        }
        req = self.server_id._request(path='/saas_server/delete_database', state=state)
        return request.redirect(req)

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
        dbs = obj.database and [obj.database] or database.get_market_dbs()
        uaddons = obj.update_addons and obj.update_addons.split(',') or []
        update_domain = [('name', 'in', uaddons)]
        iaddons = obj.install_addons and obj.install_addons.split(',') or []
        install_domain = [('name', 'in', iaddons)]
        no_update_dbs = []
        for db_name in dbs:
            try:
                registry = openerp.modules.registry.RegistryManager.get(db_name)
                with registry.cursor() as rcr:
                    # update database.uuid
                    openerp.service.db._drop_conn(rcr, db_name)
                    module = registry['ir.module.module']
                    # 1. Update existing modules
                    uaids = module.search(rcr, SUPERUSER_ID, update_domain)
                    if uaids:
                        module.button_upgrade(rcr, SUPERUSER_ID, uaids)
                    # 2. Install new modules
                    iaids = module.search(rcr, SUPERUSER_ID, install_domain)
                    if iaids:
                        module.button_immediate_install(rcr, SUPERUSER_ID, iaids)
                    # 3. Execute methods
                    for fix in obj.fix_ids:
                        getattr(registry[fix.model], fix.method)(rcr, SUPERUSER_ID)
            except:
                no_update_dbs.append(db_name)
        if no_update_dbs:
            desc = 'These databases were not updated: %s', ', '.join(no_update_dbs)
            self.write(cr, uid, obj.id, {'description': desc})
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'saas.config',
            'res_id': obj.id,
            'target': 'new',
        }


class SaasConfigFix(models.TransientModel):
    _name = 'saas.config.fix'

    model = fields.Char('Model', required=1, size=64)
    method = fields.Char('Method', required=1, size=64)
    config_id = fields.Many2one('saas.config', 'Config')
