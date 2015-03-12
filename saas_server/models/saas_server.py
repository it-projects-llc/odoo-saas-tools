import os
import openerp
from openerp import SUPERUSER_ID
from openerp import models, fields
from openerp.addons.saas_utils import connector


def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


class SaasServerPlan(models.Model):
    _name = 'saas_server.plan'

    name = fields.Char('Plan')
    template = fields.Char('Template')
    demo = fields.Boolean('Demo Data')
    sequence = fields.Integer('Sequence')
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')],
                             'State', default='draft')
    required_addons_ids = fields.Many2many('ir.module.module',
                                           rel='company_required_addons_rel',
                                           id1='company_id', id2='module_id',
                                           string='Required Addons')
    client_ids = fields.One2many('saas_server.client', 'plan_id', 'Clients')

    _order = 'sequence'

    def create_template(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        openerp.service.db.exp_create_database(obj.template, obj.demo, 'en_US')
        addon_names = [x.name for x in obj.required_addons_ids]
        if 'saas_client' not in addon_names:
            addon_names.append('saas_client')
        to_search = [('name', 'in', addon_names)]
        addon_ids = connector.call(obj.template, 'ir.module.module',
                                   'search', to_search)
        for addon_id in addon_ids:
            connector.call(obj.template, 'ir.module.module',
                           'button_immediate_install', addon_id)
        return self.write(cr, uid, obj.id, {'state': 'confirmed'})

    def delete_template(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        openerp.service.db.exp_drop(obj.template)
        return self.write(cr, uid, obj.id, {'state': 'draft'})


class SaasServerClient(models.Model):
    _name = 'saas_server.client'

    name = fields.Char('Database name', readonly=True)
    client_id = fields.Char('Client ID', readonly=True, select=True)
    users_len = fields.Integer('Count users')
    file_storage = fields.Integer('File storage (MB)')
    db_storage = fields.Integer('DB storage (MB)')
    plan_id = fields.Many2one('saas_server.plan', 'Plan')

    def update_all(self, cr, uid, server_db):
        db_list = openerp.service.db.exp_list()
        try:
            client_list.remove(server_db)
        except:
            pass

        res = []
        for db in db_list:
            registry = openerp.modules.registry.RegistryManager.get(db)
            with registry.cursor() as db_cr:
                client_id = registry['ir.config_parameter'].get_param(db_cr,
                                                SUPERUSER_ID, 'database.uuid')
                users = registry['res.users'].search(db_cr, SUPERUSER_ID,
                                                     [('share', '=', False)])
                users_len = len(users)
                data_dir = openerp.tools.config['data_dir']

                file_storage = get_size('%s/filestore/%s' % (data_dir, db))
                file_storage = int(file_storage / (1024 * 1024))

                db_cr.execute("select pg_database_size('%s')" % db)
                db_storage = db_cr.fetchone()[0]
                db_storage = int(db_storage / (1024 * 1024))

                data = {
                    'name': db,
                    'client_id': client_id,
                    'users_len': users_len,
                    'file_storage': file_storage,
                    'db_storage': db_storage,
                }
                oid = self.search(cr, uid, [('client_id', '=', client_id)])
                if not oid:
                    self.create(cr, uid, data)
                else:
                    self.write(cr, uid, oid, data)
                res.append(data)

        return res


class ResUsers(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    plan_id = fields.Many2one('saas_server.plan', 'Plan')
    organization = fields.Char('Organization', size=64)
    database = fields.Char('Database', size=64)
