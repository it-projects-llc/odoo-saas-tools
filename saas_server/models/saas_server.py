import time
import psycopg2
import random
import string

import odoo
from datetime import datetime
from odoo.service import db
from odoo.tools.translate import _
from odoo.addons.saas_base.tools import get_size
from odoo import api, models, fields, SUPERUSER_ID, exceptions
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

import logging
_logger = logging.getLogger(__name__)


def random_password(len=32):
    return ''.join(random.SystemRandom().choice(
        string.ascii_uppercase + string.digits) for _ in range(len))


class SaasServerClient(models.Model):
    _name = 'saas_server.client'
    _inherit = ['mail.thread', 'saas_base.client']

    name = fields.Char('Database name', readonly=True, required=True)
    client_id = fields.Char('Database UUID', readonly=True, index=True)
    expiration_datetime = fields.Datetime(readonly=True)
    state = fields.Selection([('template', 'Template'),
                              ('draft', 'New'),
                              ('open', 'In Progress'),
                              ('cancelled', 'Cancelled'),
                              ('pending', 'Pending'),
                              ('deleted', 'Deleted')],
                             'State', default='draft',
                             track_visibility='onchange')
    host = fields.Char('Host')

    _sql_constraints = [
        ('client_id_uniq',
         'unique (client_id)',
         'client_id should be unique!'),
    ]

    @api.multi
    def create_database(self, template_db=None, demo=False, lang='en_US'):
        self.ensure_one()
        new_db = self.name
        res = {}
        if template_db:
            db._drop_conn(self.env.cr, template_db)
            db.exp_duplicate_database(template_db, new_db)
        else:
            password = random_password()
            res.update({'superuser_password': password})
            db.exp_create_database(
                new_db, demo, lang, user_password=password)
        self.state = 'open'
        return res

    @api.multi
    def registry(self, new=False, **kwargs):
        self.ensure_one()
        m = odoo.modules.registry.Registry
        return m.new(self.name, **kwargs)

    @api.multi
    def install_addons(self, addons, is_template_db):
        self.ensure_one()
        addons = set(addons)
        addons.add('mail_delete_sent_by_footer')  # debug
        if is_template_db:
            addons.add('auth_oauth')
            addons.add('saas_client')
        else:
            addons.add('saas_client')
        if not addons:
            return
        with self.registry().cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, self._context)
            self._install_addons(env, addons)

    @api.multi
    def disable_mail_servers(self):
        '''
        disables mailserver on db to stop it from sending and receiving mails
        '''
        # let's disable incoming mail servers
        self.ensure_one()
        incoming_mail_servers = self.env['fetchmail.server'].search([])
        if len(incoming_mail_servers):
            incoming_mail_servers.write({'active': False})

        # let's disable outgoing mailservers too
        outgoing_mail_servers = self.env['ir.mail_server'].search([])
        if len(outgoing_mail_servers):
            outgoing_mail_servers.write({'active': False})

    @api.multi
    def _install_addons(self, client_env, addons):
        for addon in client_env['ir.module.module'].search([
                ('name', 'in', list(addons))]):
            addon.button_install()

    @api.multi
    def update_registry(self):
        self.ensure_one()
        self.registry(new=True, update_module=True)

    @api.multi
    def prepare_database(self, **kwargs):
        self.ensure_one()
        with self.registry().cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, self._context)
            self._prepare_database(env, **kwargs)

    @api.model
    def _config_parameters_to_copy(self):
        return ['saas_client.ab_location',
                'saas_client.ab_register',
                'saas_client.saas_dashboard']

    @api.multi
    def _prepare_database(self,
                          client_env,
                          owner_user=None,
                          is_template_db=False,
                          addons=None,
                          access_token=None,
                          tz=None,
                          server_requests_scheme='http'):
        self.ensure_one()
        if not addons:
            addons = []
        client_id = self.client_id

        # update saas_server.client state
        if is_template_db:
            self.state = 'template'

        # set tz
        if tz:
            client_env['res.users'].search([]).write({'tz': tz})
            client_env['ir.default'].set('res.partner', 'tz', tz)

        # update database.uuid
        client_env['ir.config_parameter'].sudo().set_param('database.uuid', client_id)

        # copy configs
        for key in self._config_parameters_to_copy():
            value = self.env['ir.config_parameter'].sudo(
            ).get_param(key, default='')
            client_env['ir.config_parameter'].sudo().set_param(key, value)

        # set web.base.url config
        client_env['ir.config_parameter'].sudo().set_param(
            'web.base.url', '%s://%s' % (server_requests_scheme, self.host))

        # saas_client must be already installed
        oauth_provider = client_env.ref('saas_client.saas_oauth_provider')
        if is_template_db:
            # copy auth provider from saas_server
            saas_oauth_provider = self.env.ref(
                'saas_server.saas_oauth_provider')

            oauth_provider_data = {'enabled': False, 'client_id': client_id}
            for attr in ['name', 'auth_endpoint', 'scope',
                         'validation_endpoint', 'data_endpoint',
                         'css_class', 'body', 'enabled', 'local_host',
                         'local_port']:
                oauth_provider_data[attr] = getattr(saas_oauth_provider, attr)
            oauth_provider = client_env.ref('saas_client.saas_oauth_provider')
            oauth_provider.write(oauth_provider_data)
        else:
            oauth_provider.client_id = client_id

        # prepare users
        OWNER_TEMPLATE_LOGIN = 'owner_template'
        user = None
        if is_template_db:
            client_env['res.users'].create({
                'login': OWNER_TEMPLATE_LOGIN,
                'name': 'NAME',
                'email': 'onwer-email@example.com',
            })

            client_env['res.users'].browse(SUPERUSER_ID).write({
                'oauth_provider_id': oauth_provider.id,
                'oauth_uid': SUPERUSER_ID,
                'oauth_access_token': access_token
            })
        else:
            domain = [('login', '=', OWNER_TEMPLATE_LOGIN)]
            res = client_env['res.users'].search(domain)
            if res:
                user = res[0]
                client_env['ir.config_parameter'].sudo().set_param(
                    'res.users.owner', user.id)

            portal_owner_uid = owner_user.pop('user_id')
            res = client_env['res.users'].search(
                [('oauth_uid', '=', portal_owner_uid)])
            if res:
                # user already exists (e.g. administrator)
                user = res[0]
            if not user:
                user = client_env['res.users'].browse(SUPERUSER_ID)

            vals = owner_user
            vals.update({
                'oauth_provider_id': oauth_provider.id,
                'oauth_uid': portal_owner_uid,
                'oauth_access_token': access_token,
                'country_id': owner_user.get('country_id') and
                self.env['res.country'].browse(owner_user['country_id']) and
                self.env['res.country'].browse(owner_user['country_id']).id,
            })

            user.write(vals)

    @api.model
    def update_all(self):
        self.sudo().search([]).update()

    @api.multi
    def update_one(self):
        for server in self:
            server.sudo().update()

    @api.multi
    def update(self):
        for record in self:
            try:
                registry = record.registry()
                with registry.cursor() as client_cr:
                    client_env = api.Environment(
                        client_cr, SUPERUSER_ID, record._context)
                    data = record._get_data(client_env, record.client_id)
                    record.write(data)
            except psycopg2.OperationalError:
                if record.state != 'draft':
                    record.state = 'deleted'
                return

    @api.multi
    def _get_data(self, client_env, check_client_id):
        self.ensure_one()
        client_id = client_env['ir.config_parameter'].sudo(
        ).get_param('database.uuid')
        if check_client_id != client_id:
            return {'state': 'deleted'}
        users = client_env['res.users'].search(
            [('share', '=', False), ('id', '!=', SUPERUSER_ID)])
        param_obj = client_env['ir.config_parameter']
        max_users = param_obj.sudo().get_param(
            'saas_client.max_users', '0').strip()
        suspended = param_obj.sudo().get_param(
            'saas_client.suspended', '0').strip()
        total_storage_limit = param_obj.sudo().get_param(
            'saas_client.total_storage_limit', '0').strip()
        users_len = len(users)
        data_dir = odoo.tools.config['data_dir']

        file_storage = get_size('%s/filestore/%s' % (data_dir, self.name))
        file_storage = int(file_storage / (1024 * 1024))

        client_env.cr.execute("select pg_database_size('%s')" % self.name)
        db_storage = client_env.cr.fetchone()[0]
        db_storage = int(db_storage / (1024 * 1024))

        data = {
            'client_id': client_id,
            'users_len': users_len,
            'max_users': max_users,
            'file_storage': file_storage,
            'db_storage': db_storage,
            'total_storage_limit': total_storage_limit,
        }
        if suspended == '0' and self.state == 'pending':
            data.update({'state': 'open'})
        if suspended == '1' and self.state == 'open':
            data.update({'state': 'pending'})
        return data

    @api.multi
    def upgrade_database(self, **kwargs):
        for record in self:
            with record.registry().cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, record._context)
                return record._upgrade_database(env, **kwargs)

    @api.multi
    def _upgrade_database(self, client_env, data):
        self.ensure_one()
        # "data" comes from saas_portal/models/wizard.py::upgrade_database
        post = data
        module = client_env['ir.module.module']
        print(('_upgrade_database', data))
        res = {}

        # 0. Update module list
        update_list = post.get('update_addons_list', False)
        if update_list:
            module.update_list()

        # 1. Update addons
        update_addons = post.get('update_addons', [])
        if update_addons:
            module.search([('name', 'in', update_addons)]
                          ).button_immediate_upgrade()

        # 2. Install addons
        install_addons = post.get('install_addons', [])
        if install_addons:
            module.search([('name', 'in', install_addons)]
                          ).button_immediate_install()

        # 3. Uninstall addons
        uninstall_addons = post.get('uninstall_addons', [])
        if uninstall_addons:
            module.search([('name', 'in', uninstall_addons)]
                          ).button_immediate_uninstall()

        # 4. Run fixes
        fixes = post.get('fixes', [])
        for model, method in fixes:
            getattr(self.env[model], method)()

        # 5. update parameters
        params = post.get('params', [])
        for obj in params:
            if obj['key'] == 'saas_client.expiration_datetime':
                self.expiration_datetime = obj['value']
            if obj['key'] == 'saas_client.trial' and obj['value'] == 'False':
                self.trial = False
            # groups = []
            # if obj.get('hidden'):
            #     groups = ['saas_client.group_saas_support']
            client_env['ir.config_parameter'].sudo().set_param(
                obj['key'], obj['value'] or ' ')

        # 6. Access rights
        access_owner_add = post.get('access_owner_add', [])
        owner_id = client_env['ir.config_parameter'].sudo(
        ).get_param('res.users.owner', 0)
        owner_id = int(owner_id)
        if not owner_id:
            res['owner_id'] = "Owner's user is not found"
        if access_owner_add and owner_id:
            res['access_owner_add'] = []
            for g_ref in access_owner_add:
                g = client_env.ref(g_ref, raise_if_not_found=False)
                if not g:
                    res['access_owner_add'].append(
                        'group not found: %s' % g_ref)
                    continue
                g.write({'users': [(4, owner_id, 0)]})
        access_remove = post.get('access_remove', [])
        if access_remove:
            res['access_remove'] = []
            for g_ref in access_remove:
                g = client_env.ref(g_ref, raise_if_not_found=False)
                if not g:
                    res['access_remove'].append('group not found: %s' % g_ref)
                    continue
                users = []
                for u in g.users:
                    if u.id != SUPERUSER_ID:
                        users.append((3, u.id, 0))
                g.write({'users': users})

        # 7. Configure outgoing mail
        data = post.get('configure_outgoing_mail', [])
        for mail_conf in data:
            ir_mail_server = client_env['ir.mail_server']
            ir_mail_server.create({'name': 'mailgun',
                                   'smtp_host': 'smtp.mailgun.org',
                                   'smtp_user': mail_conf['smtp_login'],
                                   'smtp_pass': mail_conf['smtp_password']})

        # 8.Limit number of records
        model_obj = client_env['ir.model']
        base_limit_records_number_obj = client_env['base.limit.records_number']
        data = post.get('limit_nuber_of_records', [])
        for limit_line in data:
            model = model_obj.search([('model', '=', limit_line['model'])])
            if model:
                limit_record = base_limit_records_number_obj.search(
                    [('model_id', '=', model.id)])
                if limit_record:
                    limit_record.update(
                        {'domain': limit_line['domain'],
                         'max_records': limit_line['max_records'], })
                else:
                    base_limit_records_number_obj.create(
                        {'name': 'limit_' + limit_line['model'],
                         'model_id': model.id,
                         'domain': limit_line['domain'],
                         'max_records': limit_line['max_records'], })
            else:
                res['limit'] = "there is no model named %s" % limit_line['model']

        return res

    @api.model
    def _cron_delete_expired_databases(self):
        now = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        res = self.search([('state', 'not in', ['deleted', 'template']),
                           ('expiration_datetime', '<=', now),
                           ('trial', '=', True)])
        _logger.info('delete_expired_databases %s', res)
        res.delete_database()

    @api.multi
    def delete_database(self):
        for record in self:
            db.exp_drop(self.name)
        self.write({'state': 'deleted'})

    @api.multi
    def rename_database(self, new_dbname):
        for record in self:
            db.exp_rename(self.name, new_dbname)
        self.name = new_dbname

    @api.model
    def _transport_backup(self, dump_db, filename=None):
        '''
        backup transport agents should override this
        '''
        raise exceptions.Warning(
            _('''Transport agent has not been configured. You need either
              install one of saas_server_backup_* or remove
              saas_portal_backup'''))

    @api.multi
    def backup_database(self):
        res = []
        for database_obj in self:
            data = {}
            data['name'] = database_obj.name

            filename = "%(db_name)s_%(timestamp)s.zip" % {
                'db_name': database_obj.name,
                'timestamp': datetime.utcnow().strftime(
                    "%Y-%m-%d_%H-%M-%SZ")}

            def dump_db(stream):
                return db.dump_db(database_obj.name, stream)

            try:
                database_obj._transport_backup(dump_db, filename=filename)
                data['status'] = 'success'
            except Exception as e:
                _logger.exception(
                    'An error happened during database %s backup' % (database_obj.name))
                data['status'] = 'fail'
                data['message'] = str(e)

            res.append(data)

        return res

    @api.model
    def restart_server(self):
        odoo.service.server.restart()
        return True
