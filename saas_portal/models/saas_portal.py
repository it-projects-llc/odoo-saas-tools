# -*- coding: utf-8 -*-
import simplejson
import werkzeug
import requests
import random
from datetime import datetime, timedelta

from odoo import api
from odoo import exceptions
from odoo import fields
from odoo import models
from odoo.tools import scan_languages
from odoo.tools.translate import _
from odoo.addons.base.res.res_partner import _tz_get
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons.saas_base.exceptions import MaximumDBException, MaximumTrialDBException

from odoo.addons.saas_base.exceptions import MaximumDBException
from werkzeug.exceptions import Forbidden

import logging
_logger = logging.getLogger(__name__)


@api.multi
def _compute_host(self):
    base_saas_domain = self.env['ir.config_parameter'].get_param('saas_portal.base_saas_domain')
    for r in self:
        host = r.name
        if base_saas_domain and '.' not in r.name:
            host = '%s.%s' % (r.name, base_saas_domain)
        r.host = host


class SaasPortalServer(models.Model):
    _name = 'saas_portal.server'
    _description = 'SaaS Server'
    _rec_name = 'name'

    _inherit = ['mail.thread']
    _inherits = {'oauth.application': 'oauth_application_id'}

    name = fields.Char('Database name', required=True)
    oauth_application_id = fields.Many2one('oauth.application', 'OAuth Application', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence')
    active = fields.Boolean('Active', default=True)
    request_scheme = fields.Selection([('http', 'http'), ('https', 'https')], 'Scheme', default='http', required=True)
    verify_ssl = fields.Boolean('Verify SSL', default=True, help="verify SSL certificates for server-side HTTPS requests, just like a web browser")
    request_port = fields.Integer('Request Port', default=80)
    client_ids = fields.One2many('saas_portal.client', 'server_id', string='Clients')
    local_host = fields.Char('Local host', help='local host or ip address of server for server-side requests')
    local_port = fields.Char('Local port', help='local tcp port of server for server-side requests')
    local_request_scheme = fields.Selection([('http', 'http'), ('https', 'https')], 'Scheme', default='http', required=True)
    host = fields.Char('Host', compute=_compute_host)
    odoo_version = fields.Char('Odoo version', readonly=True)
    password = fields.Char()
    clients_host_template = fields.Char('Template for clients host names',
                                        help='The possible dynamic parts of the host names are: {dbname}, {base_saas_domain}, {base_saas_domain_1}')

    @api.model
    def create(self, vals):
        record = super(SaasPortalServer, self).create(vals)
        record.oauth_application_id._get_access_token(create=True)
        return record

    @api.one
    def _request_params(self, path='/web', scheme=None, port=None, state={}, scope=None, client_id=None):
        scheme = scheme or self.request_scheme
        port = port or self.request_port
        scope = scope or ['userinfo', 'force_login', 'trial', 'skiptheuse']
        scope = ' '.join(scope)
        client_id = client_id or self.env['oauth.application'].generate_client_id()
        params = {
            'scope': scope,
            'state': simplejson.dumps(state),
            'redirect_uri': '{scheme}://{saas_server}:{port}{path}'.format(scheme=scheme, port=port, saas_server=self.host, path=path),
            'response_type': 'token',
            'client_id': client_id,
        }
        return params

    @api.one
    def _request(self, **kwargs):
        params = self._request_params(**kwargs)[0]
        url = '/oauth2/auth?%s' % werkzeug.url_encode(params)
        return url

    @api.multi
    def _request_server(self, path=None, scheme=None, port=None, **kwargs):
        self.ensure_one()
        scheme = scheme or self.local_request_scheme or self.request_scheme
        host = self.local_host or self.host
        port = port or self.local_port or self.request_port
        params = self._request_params(**kwargs)[0]
        access_token = self.oauth_application_id.sudo()._get_access_token(create=True)
        params.update({
            'token_type': 'Bearer',
            'access_token': access_token,
            'expires_in': 3600,
        })
        url = '{scheme}://{host}:{port}{path}'.format(scheme=scheme, host=host, port=port, path=path)
        req = requests.Request('GET', url, data=params, headers={'host': self.host})
        req_kwargs = {'verify': self.verify_ssl}
        return req.prepare(), req_kwargs

    @api.multi
    def action_redirect_to_server(self):
        r = self[0]
        url = '{scheme}://{saas_server}:{port}{path}'.format(scheme=r.request_scheme, saas_server=r.host, port=r.request_port, path='/web')
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'name': 'Redirection',
            'url': url
        }

    @api.model
    def action_sync_server_all(self):
        self.search([]).action_sync_server()
        self.env['saas_portal.client'].search([]).storage_usage_monitoring()

    @api.one
    def action_sync_server(self, updating_client_ID=None):
        state = {
            'd': self.name,
            'client_id': self.client_id,
            'updating_client_ID': updating_client_ID,
        }
        req, req_kwargs = self._request_server(path='/saas_server/sync_server', state=state, client_id=self.client_id)
        res = requests.Session().send(req, **req_kwargs)

        if not res.ok:
            raise Warning('Reason: %s \n Message: %s' % (res.reason, res.content))
        try:
            data = simplejson.loads(res.text)
        except:
            _logger.error('Error on parsing response: %s\n%s' % ([req.url, req.headers, req.body], res.text))
            raise
        for r in data:
            r['server_id'] = self.id
            client = self.env['saas_portal.client'].with_context(active_test=False).search([('client_id', '=', r.get('client_id'))])
            if not client:
                database = self.env['saas_portal.database'].search([('client_id', '=', r.get('client_id'))])
                if database:
                    database.write(r)
                    continue
                client = self.env['saas_portal.client'].create(r)
            else:
                client.write(r)
        return None

    @api.model
    def get_saas_server(self):
        saas_server_list = self.env['saas_portal.server'].sudo().search([])
        return saas_server_list[random.randint(0, len(saas_server_list) - 1)]


class SaasPortalPlan(models.Model):
    _name = 'saas_portal.plan'

    name = fields.Char('Plan', required=True)
    summary = fields.Char('Summary')
    template_id = fields.Many2one('saas_portal.database', 'Template', ondelete='restrict')
    demo = fields.Boolean('Install Demo Data')
    maximum_allowed_dbs_per_partner = fields.Integer(help='maximum allowed non-trial databases per customer', require=True, default=0)
    maximum_allowed_trial_dbs_per_partner = fields.Integer(help='maximum allowed trial databases per customer', require=True, default=0)

    max_users = fields.Char('Initial Max users', default='0', help='leave 0 for no limit')
    total_storage_limit = fields.Integer('Total storage limit (MB)', help='leave 0 for no limit')
    block_on_expiration = fields.Boolean('Block clients on expiration', default=False)
    block_on_storage_exceed = fields.Boolean('Block clients on storage exceed', default=False)

    def _get_default_lang(self):
        return self.env.lang

    def _default_tz(self):
        return self.env.user.tz

    lang = fields.Selection(scan_languages(), 'Language', default=_get_default_lang)
    tz = fields.Selection(_tz_get, 'TimeZone', default=_default_tz)
    sequence = fields.Integer('Sequence')
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')],
                             'State', compute='_get_state', store=True)
    expiration = fields.Integer('Expiration (hours)', help='time to delete database. Use for demo')
    _order = 'sequence'
    grace_period = fields.Integer('Grace period (days)', help='initial days before expiration')

    dbname_template = fields.Char('DB Names', help='Used for generating client database domain name. Use %i for numbering. Ignore if you use manually created db names', placeholder='crm-%i.odoo.com')
    server_id = fields.Many2one('saas_portal.server', string='SaaS Server',
                                ondelete='restrict',
                                help='User this saas server or choose random')

    website_description = fields.Html('Website description')
    logo = fields.Binary('Logo')

    on_create = fields.Selection([
        ('login', 'Log into just created instance'),
    ], string="Workflow on create", default='login')
    on_create_email_template = fields.Many2one('mail.template',
                                               default=lambda self: self.env.ref('saas_portal.email_template_create_saas'))

    @api.one
    @api.depends('template_id.state')
    def _get_state(self):
        if self.template_id.state == 'template':
            self.state = 'confirmed'
        else:
            self.state = 'draft'

    @api.multi
    def _new_database_vals(self, vals):
        self.ensure_one()
        vals['max_users'] = self.max_users
        vals['total_storage_limit'] = self.total_storage_limit
        vals['block_on_expiration'] = self.block_on_expiration
        vals['block_on_storage_exceed'] = self.block_on_storage_exceed
        return vals

    @api.multi
    def _prepare_owner_user_data(self, user_id):
        """
        Prepare the dict of values to update owner user data in client instalnce. This method may be
        overridden to implement custom values (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        owner_user = self.env['res.users'].browse(user_id) or self.env.user
        owner_user_data = {
            'user_id': owner_user.id,
            'login': owner_user.login,
            'name': owner_user.name,
            'email': owner_user.email,
            'password_crypt': owner_user.password_crypt,
        }
        return owner_user_data

    @api.multi
    def _get_expiration(self, trial):
        self.ensure_one()
        trial_hours = trial and self.expiration
        initial_expiration_datetime = datetime.now()
        trial_expiration_datetime = (initial_expiration_datetime + timedelta(hours=trial_hours)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return trial and trial_expiration_datetime or initial_expiration_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    @api.multi
    def create_new_database(self, **kwargs):
        return self._create_new_database(**kwargs)

    @api.multi
    def _create_new_database(self, dbname=None, client_id=None, partner_id=None, user_id=None, notify_user=True, trial=False, support_team_id=None, async=None):
        self.ensure_one()

        server = self.server_id
        if not server:
            server = self.env['saas_portal.server'].get_saas_server()

        # server.action_sync_server()
        if not partner_id and user_id:
            user = self.env['res.users'].browse(user_id)
            partner_id = user.partner_id.id

        if not trial and self.maximum_allowed_dbs_per_partner != 0:
            db_count = self.env['saas_portal.client'].search_count([('partner_id', '=', partner_id),
                                                                    ('state', '=', 'open'),
                                                                    ('plan_id', '=', self.id),
                                                                    ('trial', '=', False)])
            if db_count >= self.maximum_allowed_dbs_per_partner:
                raise MaximumDBException("Limit of databases for this plan is %(maximum)s reached" % {'maximum': self.maximum_allowed_dbs_per_partner})
        if trial and self.maximum_allowed_trial_dbs_per_partner != 0:
            trial_db_count = self.env['saas_portal.client'].search_count([('partner_id', '=', partner_id),
                                                                          ('state', '=', 'open'),
                                                                          ('plan_id', '=', self.id),
                                                                          ('trial', '=', True)])
            if trial_db_count >= self.maximum_allowed_trial_dbs_per_partner:
                raise MaximumTrialDBException("Limit of trial databases for this plan is %(maximum)s reached" % {'maximum': self.maximum_allowed_trial_dbs_per_partner})

        client_expiration = self._get_expiration(trial)
        vals = {'name': dbname or self.generate_dbname(),
                'server_id': server.id,
                'plan_id': self.id,
                'partner_id': partner_id,
                'trial': trial,
                'support_team_id': support_team_id,
                'expiration_datetime': client_expiration,
                }
        client = None
        if client_id:
            vals['client_id'] = client_id
            client = self.env['saas_portal.client'].search([('client_id', '=', client_id)])

        vals = self._new_database_vals(vals)

        if client:
            client.write(vals)
        else:
            client = self.env['saas_portal.client'].create(vals)
        client_id = client.client_id

        owner_user_data = self._prepare_owner_user_data(user_id)

        state = {
            'd': client.name,
            'public_url': client.public_url,
            'e': client_expiration,
            'r': client.public_url + 'web',
            'h': client.host,
            'owner_user': owner_user_data,
            't': client.trial,
        }
        if self.template_id:
            state.update({'db_template': self.template_id.name})
        scope = ['userinfo', 'force_login', 'trial', 'skiptheuse']
        req, req_kwargs = server._request_server(path='/saas_server/new_database',
                                                 state=state,
                                                 client_id=client_id,
                                                 scope=scope,)
        res = requests.Session().send(req, **req_kwargs)
        if res.status_code != 200:
            raise Warning('Error on request: %s\nReason: %s \n Message: %s' % (req.url, res.reason, res.content))
        data = simplejson.loads(res.text)
        params = {
            'state': data.get('state'),
            'access_token': client.oauth_application_id._get_access_token(user_id, create=True),
        }
        url = '{url}?{params}'.format(url=data.get('url'), params=werkzeug.url_encode(params))
        auth_url = url

        # send email if there is mail template record
        template = self.on_create_email_template
        if template and notify_user:
            # we have to have a user in this place (how to user without a user?)
            user = self.env['res.users'].browse(user_id)
            client.with_context(user=user).message_post_with_template(template.id, composition_mode='comment')

        client.send_params_to_client_db()
        # TODO make async call of action_sync_server here
        # client.server_id.action_sync_server()
        client.sync_client()

        return {'url': url, 'id': client.id, 'client_id': client_id, 'auth_url': auth_url}

    @api.multi
    def generate_dbname(self, raise_error=True):
        self.ensure_one()
        if not self.dbname_template:
            if raise_error:
                raise exceptions.Warning(_('Template for db name is not configured'))
            return ''
        sequence = self.env['ir.sequence'].get('saas_portal.plan')
        return self.dbname_template.replace('%i', sequence)

    @api.multi
    def create_template_button(self):
        res = self.create_template()


    @api.multi
    def create_template(self, addons=None):
        self.ensure_one()
        state = {
            'd': self.template_id.name,
            'demo': self.demo and 1 or 0,
            'addons': addons or [],
            'lang': self.lang,
            'tz': self.tz,
            'is_template_db': 1,
        }
        client_id = self.template_id.client_id
        self.template_id.server_id = self.server_id

        req, req_kwargs = self.server_id._request_server(path='/saas_server/new_database', state=state, client_id=client_id)
        res = requests.Session().send(req, **req_kwargs)

        if not res.ok:
            raise Warning('Error on request: %s\nReason: %s \n Message: %s' % (req.url, res.reason, res.content))
        try:
            data = simplejson.loads(res.text)
        except:
            _logger.error('Error on parsing response: %s\n%s' % ([req.url, req.headers, req.body], res.text))
            raise

        self.template_id.password = data.get('superuser_password')
        self.template_id.state = data.get('state')
        return data

    @api.multi
    def action_sync_server(self):
        for r in self:
            r.server_id.action_sync_server()
        return True

    @api.multi
    def edit_template(self):
        return self[0].template_id.edit_database()

    @api.multi
    def upgrade_template(self):
        return self[0].template_id.show_upgrade_wizard()

    @api.multi
    def delete_template(self):
        self.ensure_one()
        res = self.template_id.delete_database_server()
        return res


class OauthApplication(models.Model):
    _inherit = 'oauth.application'

    client_id = fields.Char('Database UUID')
    last_connection = fields.Char(compute='_get_last_connection',
                                  string='Last Connection', size=64)
    server_db_ids = fields.One2many('saas_portal.server', 'oauth_application_id', string='Server Database')
    template_db_ids = fields.One2many('saas_portal.database', 'oauth_application_id', string='Template Database')
    client_db_ids = fields.One2many('saas_portal.client', 'oauth_application_id', string='Client Database')

    @api.multi
    def _get_last_connection(self):
        for r in self:
            oat = self.env['oauth.access_token']
            to_search = [('application_id', '=', r.id)]
            access_tokens = oat.search(to_search)
            if access_tokens:
                access_token = access_tokens[0]
                r.last_connection = access_token.user_id.login_date


class SaasPortalDatabase(models.Model):
    _name = 'saas_portal.database'

    _inherits = {'oauth.application': 'oauth_application_id'}

    name = fields.Char('Database name', readonly=False)
    oauth_application_id = fields.Many2one('oauth.application', 'OAuth Application', required=True, ondelete='cascade')
    server_id = fields.Many2one('saas_portal.server', ondelete='restrict', string='Server', readonly=True)
    state = fields.Selection([('draft', 'New'),
                              ('open', 'In Progress'),
                              ('cancelled', 'Cancelled'),
                              ('pending', 'Pending'),
                              ('deleted', 'Deleted'),
                              ('template', 'Template'),
                              ],
                             'State', default='draft', track_visibility='onchange')
    host = fields.Char('Host', compute='_compute_host')
    public_url = fields.Char(compute='_compute_public_url')
    password = fields.Char()

    @api.multi
    def _compute_host(self):
        base_saas_domain = self.env['ir.config_parameter'].get_param('saas_portal.base_saas_domain')
        base_saas_domain_1 = '.'.join(base_saas_domain.rsplit('.', 2)[-2:])
        name_dict = {
            'base_saas_domain': base_saas_domain,
            'base_saas_domain_1': base_saas_domain_1,
        }
        for record in self:
            if record.server_id.clients_host_template:
                name_dict.update({'dbname': record.name})
                record.host = record.server_id.clients_host_template.format(**name_dict)
            else:
                _compute_host(self)

    @api.multi
    def _compute_public_url(self):
        for record in self:
            scheme = record.server_id.request_scheme
            host = record.host
            port = record.server_id.request_port
            public_url = "%s://%s" % (scheme, host)
            if scheme == 'http' and port != 80 or scheme == 'https' and port != 443:
                public_url = public_url + ':' + str(port)
            record.public_url = public_url + '/'

    @api.multi
    def _backup(self):
        '''
        call to backup database
        '''
        self.ensure_one()

        state = {
            'd': self.name,
            'client_id': self.client_id,
        }

        req, req_kwargs = self.server_id._request_server(path='/saas_server/backup_database', state=state, client_id=self.client_id)
        res = requests.Session().send(req, **req_kwargs)
        _logger.info('backup database: %s', res.text)
        if not res.ok:
            raise Warning('Reason: %s \n Message: %s' % (res.reason, res.content))
        data = simplejson.loads(res.text)
        if not isinstance(data[0], dict):
            raise Warning(data)
        if data[0]['status'] != 'success':
            warning = data[0].get('message', 'Could not backup database; please check your logs')
            raise Warning(warning)
        return True

    @api.one
    def action_sync_server(self):
        self.server_id.action_sync_server()

    @api.model
    def _proceed_url(self, url):
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'name': 'Redirection',
            'url': url
        }

    @api.multi
    def _request_url(self, path):
        r = self[0]
        state = {
            'd': r.name,
            'host': r.host,
            'public_url': r.public_url,
            'client_id': r.client_id,
        }
        url = r.server_id._request(path=path, state=state, client_id=r.client_id)
        return url

    @api.multi
    def _request(self, path):
        url = self._request_url(path)
        return self._proceed_url(url)

    @api.multi
    def edit_database(self):
        """Obsolete. Use saas_portal.edit_database widget instead"""
        for database_obj in self:
            return database_obj._request('/saas_server/edit_database')

    @api.multi
    def delete_database(self):
        for database_obj in self:
            return database_obj._request('/saas_server/delete_database')

    @api.multi
    def upgrade(self, payload=None):
        config_obj = self.env['saas.config']
        res = []

        if payload is not None:
            # maybe use multiprocessing here
            for database_obj in self:
                res.append(config_obj.do_upgrade_database(payload.copy(), database_obj))
        return res

    @api.one
    def delete_database_server(self, **kwargs):
        return self._delete_database_server(**kwargs)

    @api.one
    def _delete_database_server(self, force_delete=False):
        state = {
            'd': self.name,
            'client_id': self.client_id,
        }
        if force_delete:
            state['force_delete'] = 1
        req, req_kwargs = self.server_id._request_server(path='/saas_server/delete_database', state=state, client_id=self.client_id)
        res = requests.Session().send(req, **req_kwargs)
        _logger.info('delete database: %s', res.text)
        if res.status_code != 500:
            self.state = 'deleted'

    @api.multi
    def show_upgrade_wizard(self):
        obj = self[0]
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


class SaasPortalClient(models.Model):
    _name = 'saas_portal.client'
    _description = 'Client'
    _rec_name = 'name'

    _inherit = ['mail.thread', 'saas_portal.database', 'saas_base.client']

    name = fields.Char(required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', track_visibility='onchange', readonly=True)
    plan_id = fields.Many2one('saas_portal.plan', string='Plan', track_visibility='onchange', ondelete='set null', readonly=True)
    expiration_datetime = fields.Datetime(string="Expiration")
    expired = fields.Boolean('Expired')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, string='Salesperson')
    notification_sent = fields.Boolean(default=False, readonly=True, help='notification about oncoming expiration has sent')
    support_team_id = fields.Many2one('saas_portal.support_team', 'Support Team')
    active = fields.Boolean(default=True, compute='_compute_active', store=True)
    block_on_expiration = fields.Boolean('Block clients on expiration', default=False)
    block_on_storage_exceed = fields.Boolean('Block clients on storage exceed', default=False)
    storage_exceed = fields.Boolean('Storage limit has been exceed', default=False)
    trial_hours = fields.Integer('Initial period for trial (hours)',
                                 help='Subsription initial period in hours for trials',
                                 readonly=True)

    # TODO: use new api for tracking
    _track = {
        'expired': {
            'saas_portal.mt_expired':
            lambda self, cr, uid, obj, ctx=None: obj.expired
        }
    }


    @api.multi
    @api.depends('state')
    def _compute_active(self):
        for record in self:
            record.active = record.state != 'deleted'

    @api.model
    def _cron_suspend_expired_clients(self):
        payload = {
            'params': [{'key': 'saas_client.suspended', 'value': '1', 'hidden': True}],
        }
        now = fields.Datetime.now()
        expired = self.search([
            ('expiration_datetime', '<', now),
            ('expired', '=', False)
        ])
        expired.write({'expired': True})
        for record in expired:
            if record.trial or record.block_on_expiration:
                template = self.env.ref('saas_portal.email_template_has_expired_notify')
                record.message_post_with_template(template.id, composition_mode='comment')

                record.upgrade(payload)
                # if upgraded without exceptions then change the state
                record.state = 'pending'

    @api.model
    def _cron_notify_expired_clients(self):
        # send notification about expiration by email
        notification_delta = int(self.env['ir.config_parameter'].get_param('saas_portal.expiration_notify_in_advance', '0'))
        if notification_delta > 0:
            records = self.search([('expiration_datetime', '<=', (datetime.now() + timedelta(days=notification_delta)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                                   ('notification_sent', '=', False)])
            records.write({'notification_sent': True})
            for record in records:
                template = self.env.ref('saas_portal.email_template_expiration_notify')
                record.with_context(days=notification_delta).message_post_with_template(template.id, composition_mode='comment')

    def unlink(self):
        for obj in self:
            to_search1 = [('application_id', '=', obj.id)]
            tokens = self.env['oauth.access_token'].search(to_search1)
            tokens.unlink()
            # TODO: it seems we don't need stuff below
            # to_search2 = [('database', '=', obj.name)]
            # user_ids = user_model.search(to_search2)
            # if user_ids:
            #    user_model.unlink(user_ids)
            # odoo.service.db.exp_drop(obj.name)
        return super(SaasPortalClient, self).unlink()

    @api.multi
    def write(self, values):
        if 'expiration_datetime' in values:
            payload = {
                'params': [{'key': 'saas_client.expiration_datetime', 'value': values['expiration_datetime'], 'hidden': True}],
            }

            for record in self:
                record.upgrade(payload)

        result = super(SaasPortalClient, self).write(values)

        return result

    @api.multi
    def rename_database(self, new_dbname):
        self.ensure_one()
        # TODO async
        state = {
            'd': self.name,
            'client_id': self.client_id,
            'new_dbname': new_dbname,
        }
        req, req_kwargs = self.server_id._request_server(path='/saas_server/rename_database', state=state, client_id=self.client_id)
        res = requests.Session().send(req, **req_kwargs)
        _logger.info('delete database: %s', res.text)
        if res.status_code != 500:
            self.name = new_dbname

    @api.multi
    def sync_client(self):
        self.ensure_one()
        self.server_id.action_sync_server(updating_client_ID=self.client_id)

    @api.multi
    def check_partner_access(self, partner_id):
        for record in self:
            if record.partner_id.id != partner_id:
                raise Forbidden

    @api.multi
    def duplicate_database(self, dbname=None, partner_id=None, expiration=None):
        self.ensure_one()

        owner_user = self.env['res.users'].search(
            [('partner_id', '=', partner_id)], limit=1) or self.env.user

        server = self.server_id
        if not server:
            server = self.env['saas_portal.server'].get_saas_server()

        server.action_sync_server()

        vals = {'name': dbname,
                'server_id': server.id,
                'plan_id': self.plan_id.id,
                'partner_id': partner_id or self.partner_id.id,
                }
        if expiration:
            now = datetime.now()
            delta = timedelta(hours=expiration)
            vals['expiration_datetime'] = (now + delta).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        client = self.env['saas_portal.client'].create(vals)
        client_id = client.client_id

        owner_user_data = {
            'user_id': owner_user.id,
            'login': owner_user.login,
            'name': owner_user.name,
            'email': owner_user.email,
            'password': None,
        }

        state = {
            'd': client.name,
            'e': client.expiration_datetime,
            'r': client.public_url + 'web',
            'owner_user': owner_user_data,
            'public_url': client.public_url,
            'db_template': self.name,
            'disable_mail_server': True,
        }

        scope = ['userinfo', 'force_login', 'trial', 'skiptheuse']

        req, req_kwargs = server._request_server(path='/saas_server/new_database',
                                                 state=state,
                                                 client_id=client_id)
        res = requests.Session().send(req, **req_kwargs)

        if not res.ok:
            raise Warning('Reason: %s \n Message: %s' % (res.reason, res.content))
        try:
            data = simplejson.loads(res.text)
        except:
            _logger.error('Error on parsing response: %s\n%s' % ([req.url, req.headers, req.body], res.text))
            raise

        data.update({'id': client.id})

        return data

    @api.multi
    def get_upgrade_database_payload(self):
        self.ensure_one()
        return {'params': [{'key': 'saas_client.expiration_datetime', 'value': self.expiration_datetime, 'hidden': True}]}

    @api.multi
    def send_params_to_client_db(self):
        for record in self:
            payload = {
                'params': [{'key': 'saas_client.max_users', 'value': record.max_users, 'hidden': True},
                           {'key': 'saas_client.expiration_datetime', 'value': record.expiration_datetime, 'hidden': True},
                           {'key': 'saas_client.total_storage_limit', 'value': record.total_storage_limit, 'hidden': True}],
            }
            self.env['saas.config'].do_upgrade_database(payload, record)

    @api.multi
    def send_expiration_info_to_partner(self):
        for record in self:
            if record.expiration_datetime:
                template = self.env.ref('saas_portal.email_template_expiration_datetime_updated')
                record.message_post_with_template(template.id, composition_mode='comment')

    @api.multi
    def storage_usage_monitoring(self):
        payload = {
            'params': [{'key': 'saas_client.suspended', 'value': '1', 'hidden': True}],
        }
        for r in self:
            if r.total_storage_limit and r.total_storage_limit < r.file_storage + r.db_storage and r.storage_exceed is False:
                r.write({'storage_exceed': True})
                template = self.env.ref('saas_portal.email_template_storage_exceed')
                r.message_post_with_template(template.id, composition_mode='comment')

                if r.block_on_storage_exceed:
                    self.env['saas.config'].do_upgrade_database(payload, r)
            if not r.total_storage_limit or r.total_storage_limit >= r.file_storage + r.db_storage and r.storage_exceed is True:
                r.write({'storage_exceed': False})


class SaasPortalSupportTeams(models.Model):
    _name = 'saas_portal.support_team'

    _inherit = ['mail.thread']

    name = fields.Char('Team name')


class ResUsersSaaS(models.Model):
    _inherit = 'res.users'

    support_team_id = fields.Many2one('saas_portal.support_team', 'Support Team', help='Support team for SaaS')

    def __init__(self, pool, cr):
        init_res = super(ResUsersSaaS, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        self.SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        self.SELF_WRITEABLE_FIELDS.extend(['support_team_id'])
        return init_res
