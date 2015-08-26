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
from oauthlib import common as oauthlib_common
import urllib2
import simplejson
import werkzeug
import requests
import random

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
        self.create_access_token()
        return self

    @api.model
    def create_access_token(self):
        expires = datetime.now() + timedelta(seconds=60*60)
        vals = {
            'user_id': self.env.user.id,
            'scope': 'userinfo',
            'expires': expires.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'token': oauthlib_common.generate_token(),
            'application_id': self.oauth_application_id.id
        }
        return self.env['oauth.access_token'].create(vals)

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
        access_token = self.env['oauth.access_token'].sudo().search([('application_id', '=', self.oauth_application_id.id)], order='id DESC', limit=1)
        access_token = access_token[0].token
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
            client = self.env['saas_portal.client'].search([
                ('client_id', '=', r.get('client_id')),
            ])
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
    required_addons_ids = fields.Many2many('ir.module.module',
                                           relation='plan_required_addons_rel',
                                           column1='plan_id', column2='module_id',
                                           string='Required Addons')
    optional_addons_ids = fields.Many2many('ir.module.module',
                                           relation='plan_optional_addons_rel',
                                           column1='plan_id', column2='module_id',
                                           string='Optional Addons')

    _order = 'sequence'

    dbname_template = fields.Char('DB Names', help='Template for db name. Use %i for numbering. Ignore if you use manually created db names', placeholder='crm-%i.odoo.com')
    server_id = fields.Many2one('saas_portal.server', string='SaaS Server',
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

    @api.one
    def _new_database_vals(self, vals):
        if self.expiration:
            now = datetime.now()
            delta = timedelta(hours=self.expiration)
            vals['expiration_datetime'] = (now + delta).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return vals

    @api.one
    def _create_new_database(self, dbname=None, client_id=None, partner_id=None):
        server = self.server_id
        if not server:
            server = self.env['saas_portal.server'].get_saas_server()

        server.action_sync_server()

        vals = {'name': dbname or self.generate_dbname()[0],
                'server_id': server.id,
                'plan_id': self.id,
                'partner_id': partner_id,
                }
        client = None
        if client_id:
            vals['client_id'] = client_id
            client = self.env['saas_portal.client'].search([('client_id', '=', client_id)])

        vals = self._new_database_vals(vals)[0]

        if client:
            client.write(vals)
        else:
            client = self.env['saas_portal.client'].create(vals)
        client_id = client.client_id

        scheme = server.request_scheme
        port = server.request_port
        state = {
            'd': client.name,
            'e': client.expiration_datetime,
            'r': '%s://%s:%s/web' % (scheme, port, client.name),
        }
        if self.template_id:
            state.update({'db_template': self.template_id.name})
        scope = ['userinfo', 'force_login', 'trial', 'skiptheuse']
        url = server._request(path='/saas_server/new_database',
                              scheme=scheme,
                              port=port,
                              state=state,
                              client_id=client_id,
                              scope=scope,)[0]
        return url

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
        plan = self[0]
        addons = [x.name for x in plan.required_addons_ids]
        state = {
            'd': plan.template_id.name,
            'demo': plan.demo and 1 or 0,
            'addons': addons,
            'lang': plan.lang,
            'tz': plan.tz,
            'is_template_db': 1,
        }
        client_id = plan.template_id.client_id
        plan.template_id.server_id = plan.server_id
        url = plan.server_id._request(path='/saas_server/new_database', state=state, client_id=client_id)
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'name': 'Create Template',
            'url': url
        }

    @api.one
    def action_sync_server(self):
        self.server_id.action_sync_server()

    @api.multi
    def edit_template(self):
        return self[0].template_id.edit_database()

    def upgrade_template(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'saas.config',
            'target': 'new',
            'context': {
                'default_action': 'upgrade',
                'default_database': obj.template_id.name
            }
        }

    @api.multi
    def delete_template(self):
        return self[0].template_id.delete_database()

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
    server_id = fields.Many2one('saas_portal.server', string='Server', readonly=True)
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


class SaasPortalClient(models.Model):
    _name = 'saas_portal.client'
    _description = 'Client'
    _rec_name = 'name'

    _inherit = ['mail.thread', 'saas_portal.database', 'saas_base.client']

    name = fields.Char(required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', track_visibility='onchange')
    plan_id = fields.Many2one('saas_portal.plan', string='Plan', track_visibility='onchange')
    expired = fields.Boolean('Expiration', compute='_get_expired')

    @api.one
    def _get_expired(self):
        now = fields.Datetime.now()
        self.expired = self.expiration_datetime and self.expiration_datetime < now

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
