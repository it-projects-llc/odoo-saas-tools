import os
import openerp
from openerp import SUPERUSER_ID
from openerp import models, fields, Environment
from openerp.addons.saas_utils import connector, database


def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


class SaasServerClient(models.Model):
    _name = 'saas_server.client'
    _inherit = ['mail.thread']

    # TODO: make inheritance from some base class to exclude dublicating fields with saas_portal->oauth.application
    name = fields.Char('Database name', readonly=True)
    client_id = fields.Char('Client ID', readonly=True, select=True)
    users_len = fields.Integer('Count users')
    file_storage = fields.Integer('File storage (MB)')
    db_storage = fields.Integer('DB storage (MB)')
    state = fields.Selection([('template', 'Template'),
                              ('draft','New'),
                              ('open','In Progress'),
                              ('cancelled', 'Cancelled'),
                              ('pending','Pending'),
                              ('deleted','Deleted')],
                             'State', default='open', track_visibility='onchange')

    def create(self, vals):
        template_db = self._context.get('template_db')
        if template_db:
            openerp.service.db._drop_conn(self.env.cr, template_db)
            #openerp.service.db.exp_drop(new_db) # for debug
            openerp.service.db.exp_duplicate_database(template_db, self.name)
        else:
            demo = self._context.get('demo')
            lang = self._context.get('lang') or 'en_US'
            openerp.service.db.exp_create_database(new_db, demo, lang)
        res = super(SaasServerClient, self).create(vals)
        res.prepare_database()
        return res

    @api.one
    def prepare_database(self):
        registry = openerp.modules.registry.RegistryManager.get(self.name)

        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, self._context)
            self._prepare_database(env)

    @api.one
    def _prepare_database(self, client_env):
        # update database.uuid
        client_env['ir.config_parameter'].set_param(cr, SUPERUSER_ID,
                                                  'database.uuid',
                                                  client_id)
        # save auth data
        oauth_provider_data = {'enabled': False, 'client_id': client_id}
        for attr in ['name', 'auth_endpoint', 'scope', 'validation_endpoint', 'data_endpoint', 'css_class', 'body']:
            oauth_provider_data[attr] = getattr(saas_oauth_provider, attr)
        oauth_provider_id = client_env['auth.oauth.provider'].create(cr, SUPERUSER_ID, oauth_provider_data)
        client_env['ir.model.data'].create(cr, SUPERUSER_ID, {
            'name': 'saas_oauth_provider',
            'module': 'saas_server',
            'noupdate': True,
            'model': 'auth.oauth.provider',
            'res_id': oauth_provider_id,
        })
        # 1. Update company with organization
        vals = {'name': organization}
        client_env['res.company'].write(cr, SUPERUSER_ID, 1, vals)
        partner = client_env['res.company'].browse(cr, SUPERUSER_ID, 1)
        client_env['res.partner'].write(cr, SUPERUSER_ID, partner.id,
                                      {'email': admin_data['email']})
        # 2. Update user credentials
        domain = [('login', '=', template_db)]
        user_ids = client_env['res.users'].search(cr, SUPERUSER_ID, domain)
        user_id = user_ids and user_ids[0] or SUPERUSER_ID
        user = client_env['res.users'].browse(cr, SUPERUSER_ID, user_id)
        user.write({
            'login': admin_data['email'],
            'name': admin_data['name'],
            'email': admin_data['email'],
            'parent_id': partner.id,
            'oauth_provider_id': oauth_provider_id,
            'oauth_uid': admin_data['user_id'],
            'oauth_access_token': access_token
        })
        # 3. Set suffix for all sequences
        seq_ids = client_env['ir.sequence'].search(cr, SUPERUSER_ID,
                                                 [('suffix', '=', False)])
        suffix = {'suffix': client_id.split('-')[0]}
        client_env['ir.sequence'].write(cr, SUPERUSER_ID, seq_ids, suffix)
        # get action_id
        action_id = client_env['ir.model.data'].xmlid_to_res_id(cr, SUPERUSER_ID, action)

        # 4. install addons
        addons = state.get('addons')
        if addons:
            addon_ids = client_env['ir.module.module'].search(cr, SUPERUSER_ID, [('name', 'in', addons)])
            for addon_id in addon_ids:
                client_env['ir.module.module'].button_immediate_install(cr, SUPERUSER_ID, addon_id)
    


    def update_all(self, cr, uid, server_db):
        #TODO: mark database as deleted if it not found
        #TODO: add state field
        db_list = database.get_market_dbs(with_templates=False)
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
