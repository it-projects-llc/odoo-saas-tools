# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api, SUPERUSER_ID, exceptions
from openerp.addons.saas_utils import connector, database
from openerp import http
from openerp.tools import config, scan_languages
from openerp.tools.translate import _
from openerp.addons.base.res.res_partner import _tz_get
import time
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import urllib2
import simplejson
import werkzeug
import requests
import random

from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.addons.saas_base.exceptions import MaximumDBException

import logging
_logger = logging.getLogger(__name__)


class SaasPortalServer(models.Model):
    _name = 'saas_portal.server'
    _description = 'SaaS Server'
    _rec_name = 'name'

    _inherit = ['mail.thread']
    _inherits = {'oauth.application': 'oauth_application_id'}

    name = fields.Char('Database name')
    oauth_application_id = fields.Many2one('oauth.application', 'OAuth Application', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence')
    active = fields.Boolean('Active', default=True)
    request_scheme = fields.Selection([('http', 'http'), ('https', 'https')], 'Scheme', default='http', required=True)
    verify_ssl = fields.Boolean('Verify SSL', default=True, help="verify SSL certificates for HTTPS requests, just like a web browser")
    request_port = fields.Integer('Request Port', default=80)
    client_ids = fields.One2many('saas_portal.client', 'server_id', string='Clients')

    @api.model
    def create(self, vals):
        self = super(SaasPortalServer, self).create(vals)
        self.oauth_application_id._get_access_token(create=True)
        return self

    @api.one
    def _request_params(self, path='/web', scheme=None, port=None, state={}, scope=None, client_id=None):
        scheme = scheme or self.request_scheme
        port = port or self.request_port
        scope = scope or ['userinfo', 'force_login', 'trial', 'skiptheuse']
        scope = ' '.join(scope)
        client_id = client_id or self.env['saas_portal.client'].generate_client_id()
        params = {
            'scope': scope,
            'state': simplejson.dumps(state),
            'redirect_uri': '{scheme}://{saas_server}:{port}{path}'.format(scheme=scheme, port=port, saas_server=self.name, path=path),
            'response_type': 'token',
            'client_id': client_id,
        }
        return params

    @api.one
    def _request(self, **kwargs):
        params = self._request_params(**kwargs)[0]
        url = '/oauth2/auth?%s' % werkzeug.url_encode(params)
        return url

    @api.one
    def _request_server(self, path=None, scheme=None, port=None, **kwargs):
        scheme = scheme or self.request_scheme
        port = port or self.request_port
        params = self._request_params(**kwargs)[0]
        access_token = self.oauth_application_id.sudo()._get_access_token(create=True)
        params.update({
            'token_type': 'Bearer',
            'access_token': access_token,
            'expires_in': 3600,
        })
        url = '{scheme}://{saas_server}:{port}{path}?{params}'.format(scheme=scheme, saas_server=self.name, port=port, path=path, params=werkzeug.url_encode(params))
        return url

    @api.multi
    def action_redirect_to_server(self):
        r = self[0]
        url = '{scheme}://{saas_server}:{port}{path}'.format(scheme=r.request_scheme, saas_server=r.name, port=r.request_port, path='/web')
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
    def action_sync_server(self):
        state = {
            'd': self.name,
            'client_id': self.client_id,
        }
        url = self._request_server(path='/saas_server/sync_server', state=state, client_id=self.client_id)[0]
        res = requests.get(url, verify=(self.request_scheme == 'https' and self.verify_ssl))
        if res.ok != True:
            msg = """Status Code - %s
Reason - %s
URL - %s
            """ % (res.status_code, res.reason, res.url)            
            raise Warning(msg)
        data = simplejson.loads(res.text)
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
    template_id = fields.Many2one('saas_portal.database', 'Template')
    demo = fields.Boolean('Install Demo Data')
    maximum_allowed_db_per_partner = fields.Integer(help='maximum allowed databases per customer', default=0)

    max_users = fields.Char('Max users allowed')
    total_storage_limit = fields.Integer('Total storage limit (MB)')
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

    dbname_template = fields.Char('DB Names', help='Template for db name. Use %i for numbering. Ignore if you use manually created db names', placeholder='crm-%i.odoo.com')
    server_id = fields.Many2one('saas_portal.server', string='SaaS Server',
                                ondelete='restrict',
                                help='User this saas server or choose random')
    
    website_description = fields.Text('Website description')
    logo = fields.Binary('Logo')

    @api.one
    @api.depends('template_id.state')
    def _get_state(self):
        if self.template_id.state == 'template':
            self.state = 'confirmed'
        else:
            self.state = 'draft'

    @api.multi
    def create_new_database(self, dbname=None, client_id=None, partner_id=None, user_id=None, notify_user=False, trial=False, support_team_id=None):
        self.ensure_one()
        db_count = self.env['saas_portal.client'].search_count([('partner_id', '=', partner_id),
                                                                ('state', '=', 'open'),
                                                                ('plan_id', '=', self.id)])
        if self.maximum_allowed_db_per_partner != 0 and db_count >= self.maximum_allowed_db_per_partner:
            raise MaximumDBException

        server = self.server_id
        if not server:
            server = self.env['saas_portal.server'].get_saas_server()

        server.action_sync_server()

        vals = {'name': dbname or self.generate_dbname()[0],
                'server_id': server.id,
                'plan_id': self.id,
                'partner_id': partner_id,
                'trial': trial,
                'support_team_id': support_team_id,
                'max_users': self.max_users,
                'total_storage_limit': self.total_storage_limit,
                'block_on_expiration': self.block_on_expiration,
                'block_on_storage_exceed': self.block_on_storage_exceed
                }
        client = None
        if client_id:
            vals['client_id'] = client_id
            client = self.env['saas_portal.client'].search([('client_id', '=', client_id)])

        if client:
            client.write(vals)
        else:
            client = self.env['saas_portal.client'].create(vals)
        client_id = client.client_id

        scheme = server.request_scheme
        port = server.request_port
        if user_id:
            owner_user = self.env['res.users'].browse(user_id)
        else:
            owner_user = self.env.user
        owner_user_data = {
            'user_id': owner_user.id,
            'login': owner_user.login,
            'name': owner_user.name,
            'email': owner_user.email,
        }
        state = {
            'd': client.name,
            'e': client.expiration_datetime,
            'r': '%s://%s:%s/web' % (scheme, client.name, port),
            'owner_user': owner_user_data,
            't': client.trial,
        }
        if self.template_id:
            state.update({'db_template': self.template_id.name})
        scope = ['userinfo', 'force_login', 'trial', 'skiptheuse']
        url = server._request_server(path='/saas_server/new_database',
                              scheme=scheme,
                              port=port,
                              state=state,
                              client_id=client_id,
                              scope=scope,)[0]
        res = requests.get(url, verify=(self.server_id.request_scheme == 'https' and self.server_id.verify_ssl))
        if res.status_code != 200:
            # TODO /saas_server/new_database show more details here
            raise exceptions.Warning('Error %s' % res.status_code)
        data = simplejson.loads(res.text)
        params = {
            'state': data.get('state'),
            'access_token': client.oauth_application_id._get_access_token(user_id, create=True),
        }
        url = '{url}?{params}'.format(url=data.get('url'), params=werkzeug.url_encode(params))

        # send email
        if notify_user:
            template = self.env.ref('saas_portal.email_template_create_saas')
            email_ctx = {
                'default_model': 'saas_portal.client',
                'default_res_id': client.id,
                'default_use_template': bool(template),
                'default_template_id': template.id,
                'default_composition_mode': 'comment',

            }
            composer = self.env['mail.compose.message'].with_context(email_ctx).create({})
            composer.send_mail()

        client.send_params_to_client_db()
        client.server_id.action_sync_server()

        return {'url': url, 'id': client.id, 'client_id': client_id}

    @api.one
    def generate_dbname(self, raise_error=True):
        if not self.dbname_template:
            if raise_error:
                raise exceptions.Warning(_('Template for db name is not configured'))
            return ''
        sequence = self.env['ir.sequence'].get('saas_portal.plan')
        return self.dbname_template.replace('%i', sequence)

    @api.multi
    def create_template(self):
        assert len(self)==1, 'This method is applied only for single record'
        # TODO use create_new_database function
        plan = self[0]
        state = {
            'd': plan.template_id.name,
            'demo': plan.demo and 1 or 0,
            'addons': [],
            'lang': plan.lang,
            'tz': plan.tz,
            'is_template_db': 1,
        }
        client_id = plan.template_id.client_id
        plan.template_id.server_id = plan.server_id
        params = plan.server_id._request_params(path='/saas_server/new_database', state=state, client_id=client_id)[0]

        access_token = plan.template_id.oauth_application_id.sudo()._get_access_token(create=True)
        params.update({
            'token_type': 'Bearer',
            'access_token': access_token,
            'expires_in': 3600,
        })
        url = '{scheme}://{saas_server}:{port}{path}?{params}'.format(scheme=plan.server_id.request_scheme,
                                                                      saas_server=plan.server_id.name,
                                                                      port=plan.server_id.request_port,
                                                                      path='/saas_server/new_database',
                                                                      params=werkzeug.url_encode(params))
        res = requests.get(url, verify=(plan.server_id.request_scheme == 'https' and plan.server_id.verify_ssl))
        if res.ok != True:
            msg = """Status Code - %s
Reason - %s
URL - %s
            """ % (res.status_code, res.reason, res.url)
            raise Warning(msg)
        return self.action_sync_server()

    @api.one
    def action_sync_server(self):
        self.server_id.action_sync_server()

    @api.multi
    def edit_template(self):
        return self[0].template_id.edit_database()

    @api.multi
    def upgrade_template(self):
        return self[0].template_id.upgrade_database()

    @api.multi
    def delete_template(self):
        res = self[0].template_id.delete_database()
        return res


class OauthApplication(models.Model):
    _inherit = 'oauth.application'

    client_id = fields.Char('Database UUID')
    last_connection = fields.Char(compute='_get_last_connection',
                                  string='Last Connection', size=64)

    @api.one
    def _get_last_connection(self):
        oat = self.pool.get('oauth.access_token')
        to_search = [('application_id', '=', self.id)]
        access_token_ids = oat.search(self.env.cr, self.env.uid, to_search)
        if access_token_ids:
            access_token = oat.browse(self.env.cr, self.env.uid,
                                      access_token_ids[0])
            self.last_connection = access_token.user_id.login_date


class SaasPortalDatabase(models.Model):
    _name = 'saas_portal.database'

    _inherits = {'oauth.application': 'oauth_application_id'}

    name = fields.Char('Database name', readonly=False)
    oauth_application_id = fields.Many2one('oauth.application', 'OAuth Application', required=True, ondelete='cascade')
    server_id = fields.Many2one('saas_portal.server', ondelete='restrict', string='Server', readonly=True)
    state = fields.Selection([('draft','New'),
                              ('open','In Progress'),
                              ('cancelled', 'Cancelled'),
                              ('pending','Pending'),
                              ('deleted','Deleted'),
                              ('template','Template'),
                          ],
                             'State', default='draft', track_visibility='onchange')

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
    def _request(self, path):
        r = self[0]
        state = {
            'd': r.name,
            'client_id': r.client_id,
        }
        url = r.server_id._request(path=path, state=state, client_id=r.client_id)
        return self._proceed_url(url)

    @api.multi
    def edit_database(self):
        return self._request('/saas_server/edit_database')

    @api.multi
    def delete_database(self):
        return self._request('/saas_server/delete_database')

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
        url = self.server_id._request_server(path='/saas_server/delete_database', state=state, client_id=self.client_id)[0]
        res = requests.get(url, verify=(self.server_id.request_scheme == 'https' and self.server_id.verify_ssl))
        _logger.info('delete database: %s', res.text)
        if res.status_code != 500:
            self.state = 'deleted'

    @api.multi
    def upgrade_database(self):
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
    partner_id = fields.Many2one('res.partner', string='Partner', track_visibility='onchange')
    plan_id = fields.Many2one('saas_portal.plan', string='Plan', track_visibility='onchange')
    expired = fields.Boolean('Expired', default=False, readonly=True)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, string='Salesperson')
    notification_sent = fields.Boolean(default=False, readonly=True, help='notification about oncoming expiration has sent')
    support_team_id = fields.Many2one('saas_portal.support_team', 'Support Team')
    expiration_datetime_sent = fields.Datetime(help='updates every time send_expiration_info_to_client_db is executed')
    active = fields.Boolean(default=True, compute='_compute_active', store=True)
    block_on_expiration = fields.Boolean('Block clients on expiration', default=False)
    block_on_storage_exceed = fields.Boolean('Block clients on storage exceed', default=False)
    storage_exceed = fields.Boolean('Storage limit has been exceed', default=False)

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
                email_ctx = {
                    'default_model': 'saas_portal.client',
                    'default_res_id': record.id,
                    'default_use_template': bool(template),
                    'default_template_id': template.id,
                    'default_composition_mode': 'comment',
                }
                composer = self.env['mail.compose.message'].with_context(email_ctx).create({})
                composer.send_mail()

                self.env['saas.config'].do_upgrade_database(payload, record.id)

    @api.model
    def _cron_notify_expired_clients(self):
        # send notification about expiration by email
        notification_delta = int(self.env['ir.config_parameter'].get_param('saas.expiration_notify_in_advance', '0'))
        if notification_delta > 0:
            records = self.search([('expiration_datetime', '<=', (datetime.now() + timedelta(days=notification_delta)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                                   ('notification_sent', '=', False)])
            records.write({'notification_sent': True})
            for record in records:
                template = self.env.ref('saas_portal.email_template_expiration_notify')
                email_ctx = {
                    'default_model': 'saas_portal.client',
                    'default_res_id': record.id,
                    'default_use_template': bool(template),
                    'default_template_id': template.id,
                    'default_composition_mode': 'comment',
                }
                composer = self.env['mail.compose.message'].with_context(email_ctx).create({})
                composer.send_mail()


    def unlink(self, cr, uid, ids, context=None):
        user_model = self.pool.get('res.users')
        token_model = self.pool.get('oauth.access_token')
        for obj in self.browse(cr, uid, ids):
            to_search1 = [('application_id', '=', obj.id)]
            tk_ids = token_model.search(cr, uid, to_search1, context=context)
            if tk_ids:
                token_model.unlink(cr, uid, tk_ids)
            # TODO: it seems we don't need stuff below
            #to_search2 = [('database', '=', obj.name)]
            #user_ids = user_model.search(cr, uid, to_search2, context=context)
            #if user_ids:
            #    user_model.unlink(cr, uid, user_ids)
            #openerp.service.db.exp_drop(obj.name)
        return super(SaasPortalClient, self).unlink(cr, uid, ids, context)

    @api.multi
    def rename_database(self, new_dbname):
        self.ensure_one()
        # TODO async
        state = {
            'd': self.name,
            'client_id': self.client_id,
            'new_dbname': new_dbname,
        }
        url = self.server_id._request_server(path='/saas_server/rename_database', state=state, client_id=self.client_id)[0]
        res = requests.get(url, verify=(self.server_id.request_scheme == 'https' and self.server_id.verify_ssl))
        _logger.info('delete database: %s', res.text)
        if res.status_code != 500:
            self.name = new_dbname

    @api.one
    def duplicate_database(self, dbname=None, partner_id=None, expiration=None):
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

        scheme = server.request_scheme
        port = server.request_port
        state = {
            'd': client.name,
            'e': client.expiration_datetime,
            'r': '%s://%s:%s/web' % (scheme, port, client.name),
        }
        state.update({'db_template': self.name,
                      'disable_mail_server' : True})
        scope = ['userinfo', 'force_login', 'trial', 'skiptheuse']
        # TODO use _request_server
        url = server._request(path='/saas_server/new_database',
                              scheme=scheme,
                              port=port,
                              state=state,
                              client_id=client_id,
                              scope=scope,)[0]
        return url

    @api.multi
    def send_expiration_info(self):
        for record in self:
            if record.expiration_datetime_sent and record.expiration_datetime and record.expiration_datetime_sent != record.expiration_datetime:
                record.expiration_datetime_sent = record.expiration_datetime
                record.send_expiration_info_to_client_db()
                record.send_expiration_info_to_partner()
                # expiration date has been changed, flush expiration notification flag
                record.notification_sent = False
            else:
                record.expiration_datetime_sent = record.expiration_datetime

    @api.multi
    def send_expiration_info_to_client_db(self):
        for record in self:
            if record.expiration_datetime:
                payload = {
                    'params': [{'key': 'saas_client.expiration_datetime', 'value': record.expiration_datetime, 'hidden': True}],
                }
                self.env['saas.config'].do_upgrade_database(payload, record.id)

    @api.multi
    def send_params_to_client_db(self):
        for record in self:
            payload = {
                'params': [{'key': 'saas_client.max_users', 'value': record.max_users, 'hidden': True},
                           {'key': 'saas_client.expiration_datetime', 'value': record.expiration_datetime, 'hidden': True},
                           {'key': 'saas_client.total_storage_limit', 'value': record.total_storage_limit, 'hidden': True}],
            }
            self.env['saas.config'].do_upgrade_database(payload, record.id)

    @api.multi
    def send_expiration_info_to_partner(self):
        for record in self:
            if record.expiration_datetime:
                template = self.env.ref('saas_portal.email_template_expiration_datetime_updated')
                email_ctx = {
                    'default_model': 'saas_portal.client',
                    'default_res_id': record.id,
                    'default_use_template': bool(template),
                    'default_template_id': template.id,
                    'default_composition_mode': 'comment',
                }
                composer = self.env['mail.compose.message'].with_context(email_ctx).create({})
                composer.send_mail()

    @api.one
    def write(self, vals):
        if 'expiration_datetime' in vals and vals['expiration_datetime']:
            self.send_expiration_info_to_client_db()
        result = super(SaasPortalClient, self).write(vals)
        return result

    @api.multi
    def storage_usage_monitoring(self):
        payload = {
            'params': [{'key': 'saas_client.suspended', 'value': '1', 'hidden': True}],
        }
        for r in self:
            if r.total_storage_limit < r.file_storage + r.db_storage and r.storage_exceed is False:
                r.write({'storage_exceed': True})
                template = self.env.ref('saas_portal.email_template_storage_exceed')
                email_ctx = {
                    'default_model': 'saas_portal.client',
                    'default_res_id': r.id,
                    'default_use_template': bool(template),
                    'default_template_id': template.id,
                    'default_composition_mode': 'comment',
                }
                composer = self.env['mail.compose.message'].with_context(email_ctx).create({})
                composer.send_mail()

                if r.block_on_storage_exceed:
                    self.env['saas.config'].do_upgrade_database(payload, r.id)


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
