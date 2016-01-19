import os
import time
import openerp
from openerp import api, models, fields, SUPERUSER_ID, exceptions
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import psycopg2
import random
import string


import logging
_logger = logging.getLogger(__name__)


def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


class SaasServerClient(models.Model):
    _name = 'saas_server.client'
    _inherit = ['mail.thread', 'saas_base.client']

    name = fields.Char('Database name', readonly=True)
    client_id = fields.Char('Database UUID', readonly=True, select=True)
    state = fields.Selection([('template', 'Template'),
                              ('draft','New'),
                              ('open','In Progress'),
                              ('cancelled', 'Cancelled'),
                              ('pending','Pending'),
                              ('deleted','Deleted')],
                             'State', default='draft', track_visibility='onchange')

    _sql_constraints = [
        ('client_id_uniq', 'unique (client_id)', 'client_id should be unique!'),
    ]

    @api.one
    def create_database(self, template_db=None, demo=False, lang='en_US'):
        new_db = self.name
        if template_db:
            openerp.service.db._drop_conn(self.env.cr, template_db)
            openerp.service.db.exp_duplicate_database(template_db, new_db)
        else:
            password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(32))
            openerp.service.db.exp_create_database(new_db, demo, lang, user_password=password)
        self.state = 'open'

    @api.one
    def registry(self, new=False, **kwargs):
        m = openerp.modules.registry.RegistryManager
        if new:
            return m.new(self.name, **kwargs)
        else:
            return m.get(self.name, **kwargs)

    @api.one
    def install_addons(self, addons, is_template_db):
        addons = set(addons)
        addons.add('mail_delete_sent_by_footer')  # debug
        if is_template_db:
            addons.add('auth_oauth')
            addons.add('saas_client')
        else:
            addons.add('saas_client')
        if not addons:
            return
        with self.registry()[0].cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, self._context)
            self._install_addons(env, addons)
    @api.one
    def disable_mail_servers(self):
        '''
        disables mailserver on db to stop it from sending and receiving mails
        '''
        # let's disable incoming mail servers
        incoming_mail_servers = self.env['fetchmail.server'].search([])
        if len(incoming_mail_servers):
            incoming_mail_servers.write({'active': False})
            
        # let's disable outgoing mailservers too
        outgoing_mail_servers = self.env['ir.mail_server'].search([])
        if len(outgoing_mail_servers):
            outgoing_mail_servers.write({'active': False})

    @api.one
    def _install_addons(self, client_env, addons):
        for addon in client_env['ir.module.module'].search([('name', 'in', list(addons))]):
            addon.button_install()

    @api.one
    def update_registry(self):
        self.registry(new=True, update_module=True)

    @api.one
    def prepare_database(self, **kwargs):
        with self.registry()[0].cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, self._context)
            self._prepare_database(env, **kwargs)

    @api.model
    def _config_parameters_to_copy(self):
        return ['saas_client.ab_location', 'saas_client.ab_register']

    @api.one
    def _prepare_database(self, client_env, owner_user=None,
                          is_template_db=False, addons=[], access_token=None,
                          tz=None, company_data={}):
        client_id = self.client_id

        # update saas_server.client state
        if is_template_db:
            self.state = 'template'

        # set tz
        if tz:
            client_env['res.users'].search([]).write({'tz': tz})
            client_env['ir.values'].set_default('res.partner', 'tz', tz)

        # update database.uuid
        client_env['ir.config_parameter'].set_param('database.uuid', client_id)

        # copy configs
        for key in self._config_parameters_to_copy():
            value = self.env['ir.config_parameter'].get_param(key, default='')
            client_env['ir.config_parameter'].set_param(key, value)

        # copy auth provider from saas_server
        saas_oauth_provider = self.env.ref('saas_server.saas_oauth_provider')
        oauth_provider = None
        if is_template_db and not client_env.ref('saas_server.saas_oauth_provider', raise_if_not_found=False):
            oauth_provider_data = {'enabled': False, 'client_id': client_id}
            for attr in ['name', 'auth_endpoint', 'scope', 'validation_endpoint', 'data_endpoint', 'css_class', 'body', 'enabled']:
                oauth_provider_data[attr] = getattr(saas_oauth_provider, attr)
            oauth_provider = client_env['auth.oauth.provider'].create(oauth_provider_data)
            client_env['ir.model.data'].create({
                'name': 'saas_oauth_provider',
                'module': 'saas_server',
                'noupdate': True,
                'model': 'auth.oauth.provider',
                'res_id': oauth_provider.id,
            })
        if not oauth_provider:
            oauth_provider = client_env.ref('saas_server.saas_oauth_provider')

        if not is_template_db:
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
            res = client_env['res.users'].search([('oauth_uid', '=', owner_user['user_id'])])
            if res:
                # user already exists (e.g. administrator)
                user = res[0]
            if not user:
                user = client_env['res.users'].browse(SUPERUSER_ID)
            user.write({
                'login': owner_user['login'],
                'name': owner_user['name'],
                'email': owner_user['email'],
                'oauth_provider_id': oauth_provider.id,
                'oauth_uid': owner_user['user_id'],
                'oauth_access_token': access_token
            })

            oauth_provider.write({'enabled': True})

            if isinstance(company_data, dict) and \
                    company_data.get("name", False):
                company = client_env['ir.model.data'].xmlid_to_object(
                    "base.main_company")
                company.write({"name": company_data['company']})
                company.partner_id.write(company_data)

    @api.model
    def update_all(self):
        self.sudo().search([]).update()

    @api.one
    def update(self):
        try:
            registry = self.registry()[0]
        except psycopg2.OperationalError:
            if self.state != 'draft':
                self.state = 'deleted'
            return
        with registry.cursor() as client_cr:
            client_env = api.Environment(client_cr, SUPERUSER_ID, self._context)
            data = self._get_data(client_env, self.client_id)[0]
            self.write(data)

    @api.one
    def _get_data(self, client_env, check_client_id):
        client_id = client_env['ir.config_parameter'].get_param('database.uuid')
        if check_client_id != client_id:
            return {'state': 'deleted'}
        users = client_env['res.users'].search([('share', '=', False)])
        users_len = len(users)
        data_dir = openerp.tools.config['data_dir']

        file_storage = get_size('%s/filestore/%s' % (data_dir, self.name))
        file_storage = int(file_storage / (1024 * 1024))

        client_env.cr.execute("select pg_database_size('%s')" % self.name)
        db_storage = client_env.cr.fetchone()[0]
        db_storage = int(db_storage / (1024 * 1024))

        data = {
            'client_id': client_id,
            'users_len': users_len,
            'file_storage': file_storage,
            'db_storage': db_storage,
        }
        return data

    @api.one
    def upgrade_database(self, **kwargs):
        with self.registry()[0].cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, self._context)
            return self._upgrade_database(env, **kwargs)[0]


    @api.one
    def _upgrade_database(self, client_env, data):
        # "data" comes from saas_portal/models/wizard.py::upgrade_database
        post = data
        module = client_env['ir.module.module']
        print '_upgrade_database', data
        
        # 0. Update module list
        update_list = post.get('update_addons_list', False)
        if update_list:
            module.update_list()
            
        # 1. Update addons
        update_addons = post.get('update_addons', [])
        if update_addons:
            module.search([('name', 'in', update_addons)]).button_immediate_upgrade()

        # 2. Install addons
        install_addons = post.get('install_addons', [])
        if install_addons:
            module.search([('name', 'in', install_addons)]).button_immediate_install()

        # 3. Uninstall addons
        uninstall_addons = post.get('uninstall_addons', [])
        if uninstall_addons:
            module.search([('name', 'in', uninstall_addons)]).button_immediate_uninstall()

        # 4. Run fixes
        fixes = post.get('fixes', [])
        for model, method in fixes:
            getattr(request.registry[model], method)()

        # 5. update parameters
        params = post.get('params', [])
        for obj in params:
            groups = []
            if obj.get('hidden'):
                groups = ['saas_client.group_saas_support']
            client_env['ir.config_parameter'].set_param(obj['key'], obj['value'], groups=groups)
        return 'OK'

    @api.model
    def delete_expired_databases(self):
        now = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        res = self.search([('state','not in', ['deleted']), ('expiration_datetime', '<=', now)])
        _logger.info('delete_expired_databases %s', res)
        res.delete_database()

    @api.one
    def delete_database(self):
        openerp.service.db.exp_drop(self.name)
        self.write({'state': 'deleted'})

    @api.one
    def disable_database(self):
        with self.registry()[0].cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, self._context)
            return self._disable_database(env)[0]

    @api.one
    def _disable_database(self, client_env):
        icp = client_env['ir.config_parameter']
        users_model = client_env['res.users']

        # First we save the current state
        state_model = self.env['saas_server.client.state']
        domain = [('client_id', '=', self.client_id)]
        state = state_model.search(domain)
        if not state:
            state = state_model.create({'client_id': self.client_id})
        else:
            if state.disabled:
                return 'Already disabled'
        state.signup = bool(icp.get_param('auth_signup.allow_uninvited',
                                          default='False'))

        users = users_model.search([])
        to_disable = [x.id for x in users if x.id != SUPERUSER_ID]
        _logger.info("\n\nUsers to disable: %s\n", to_disable)
        state.set_users(to_disable)

        # Then we disable signup and login
        icp.set_param('auth_signup.allow_uninvited', 'False')
        users = users_model.search([('id', 'in', to_disable)])
        for user in users:
            _logger.info("Disabling user <%s: %s>", user.id, user.login)
            user.active = False

        state.disabled = True
        return 'OK'

    @api.one
    def enable_database(self):
        with self.registry()[0].cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, self._context)
            return self._enable_database(env)[0]

    @api.one
    def _enable_database(self, client_env):
        icp = client_env['ir.config_parameter']
        users_model = client_env['res.users']

        state_model = self.env['saas_server.client.state']
        domain = [('client_id', '=', self.client_id)]
        state = state_model.search(domain)
        if not state.disabled:
            return 'Not disabled'

        icp.set_param('auth_signup.allow_uninvited', str(state.signup))

        disabled = state.get_users()
        if isinstance(disabled, list) and \
                disabled[0] and \
                isinstance(disabled[0], list):
            disabled = disabled[0]

        domain = [('id', 'in', disabled)]
        users = users_model.search(domain)
        for user in users:
            _logger.info("Enabling user <%s: %s>", user.id, user.login)
            user.active = True

        state.disabled = False
        return 'OK'


class SaasServerClientState(models.Model):
    _name = 'saas_server.client.state'

    client_id = fields.Char()
    disabled = fields.Boolean(default=False)
    signup = fields.Boolean()
    users = fields.Char()

    _sql_constraints = [
        ('client_id_uniq', 'unique (client_id)', 'client_id should be unique!'),
    ]

    @api.one
    def set_users(self, ids):
        if not isinstance(ids, list):
            ids = [ids]
        self.users = ",".join([str(i) for i in ids])

    @api.one
    def get_users(self):
        return [int(x) for x in self.users.split(",")]
