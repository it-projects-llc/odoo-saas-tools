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
import uuid
import werkzeug
import requests
import random

import logging
_logger = logging.getLogger(__name__)

class SaasPortalServer(models.Model):
    _name = 'saas_portal.server'
    _description = 'SaaS Server'

    _inherit = ['mail.thread']

    name = fields.Char('Database Name', required=True)
    sequence = fields.Integer('Sequence')
    active = fields.Boolean('Active', default=True)
    https = fields.Boolean('HTTPS', default=False)
    client_ids = fields.One2many('oauth.application', 'server_id', string='Clients')

    @api.one
    def _request_params(self, path='/web', scheme='http', state={}, scope=None, client_id=None):
        scope = scope or ['userinfo', 'force_login', 'trial', 'skiptheuse']
        scope = ' '.join(scope)
        client_id = client_id or self.env['oauth.application'].generate_client_id()
        params = {
            'scope': scope,
            'state': simplejson.dumps(state),
            'redirect_uri': '{scheme}://{saas_server}{path}'.format(scheme=scheme, saas_server=self.name, path=path),
            'response_type': 'token',
            'client_id': client_id,
        }
        return params

    @api.one
    def _request(self, add_host=False, **kwargs):
        params = self._request_params(**kwargs)[0]
        url = '/oauth2/auth?%s' % werkzeug.url_encode(params)
        if add_host:
            domain = self.env['ir.config_parameter'].get_param('saas_portal.base_saas_domain')
            scheme = 'http'
            url = '{scheme}://{domain}{url}'.format(scheme=scheme, domain=domain, url=url)
        return url

    @api.one
    def _request_server(self, path=None, scheme='http', **kwargs):
        params = self._request_params(**kwargs)[0]
        access_token = self.env['oauth.access_token'].sudo().search([('user_id', '=', self.env.user.id)], order='id DESC', limit=1)
        access_token = access_token[0].token
        params.update({
            'token_type': 'Bearer',
            'access_token': access_token,
            'expires_in': 3600,
        })
        url = '{scheme}://{saas_server}{path}?{params}'.format(scheme=scheme, saas_server=self.name, path=path, params=werkzeug.url_encode(params))
        return url

    @api.model
    def action_update_stats_all(self):
        self.search([]).action_update_stats()

    @api.one
    def action_update_stats(self):
        scheme = 'https' if self.https else 'http'
        url = '{scheme}://{domain}/saas_server/stats'.format(scheme=scheme, domain=self.name)
        data = urllib2.urlopen(url).read()
        data = simplejson.loads(data)
        for r in data:
            r['server_id'] = self.id
            client = self.env['oauth.application'].search([
                '|',
                ('client_id', '=', r.get('client_id')),
                ('name', '=', r.get('name'))
            ])
            if not client:
                client = self.env['oauth.application'].create(r)
            elif client.name == r.get('name') and client.client_id != r.get('client_id') and client.state != 'deleted':
                raise exceptions.Warning(_('Client with that name already exists: %s') % client.name)
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
    template_id = fields.Many2one('oauth.application', 'Template DB')
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
    expiration = fields.Integer('Expiration (hours)', help='time to delete databse. Use for demo')
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
    def _create_new_database(self, scheme='http', dbname=None, client_id=None, partner_id=None):
        server = self.server_id
        if not server:
            server = self.env['saas_portal.server'].get_saas_server()

        vals = {'name': dbname or self.generate_dbname()[0],
                'server_id': server.id,
                'plan_id': self.id,
                'partner_id': partner_id,
                }
        client = self.env['oauth.application'].search([('name', '=', vals.get('name')), ('state', '=', 'deleted')])

        if client_id:
            vals['client_id'] = client_id

        vals = self._new_database_vals(vals)[0]

        if client:
            client.write(vals)
        else:
            client = self.env['oauth.application'].create(vals)
        client_id = client.client_id

        state = {
            'd': client.name,
            'r': '%s://%s/web' % (scheme, client.name),
            'db_template': self.template_id.name,
        }
        scope = ['userinfo', 'force_login', 'trial', 'skiptheuse']
        url = server._request(path='/saas_server/new_database',
                              scheme=scheme,
                              state=state,
                              client_id=client_id,
                              scope=scope,)[0]
        return url

    @api.one
    def generate_dbname(self, raise_error=True):
        # TODO make more elegant solution
        if not self.dbname_template:
            if raise_error:
                raise exceptions.Warning(_('Template for db name is not configured'))
            return ''
        id = str(random.randint(100, 10000))
        id = '4918'  # debug
        return self.dbname_template.replace('%i', id)

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
    def action_update_stats(self):
        self.server_id.action_update_stats()

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
        return self[0].template_id.delete_db()


class OauthApplication(models.Model):
    _name = 'oauth.application'
    _description = 'Client'

    _inherit = ['oauth.application', 'mail.thread']

    @api.model
    def generate_client_id(self):
        return str(uuid.uuid1())

    name = fields.Char('Database name', readonly=False, required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', track_visibility='onchange')
    plan_id = fields.Many2one('saas_portal.plan', string='Plan', track_visibility='onchange')
    client_id = fields.Char('Client ID', readonly=True, select=True, default=generate_client_id)
    users_len = fields.Integer('Count users', readonly=True)
    file_storage = fields.Integer('File storage (MB)', readonly=True)
    db_storage = fields.Integer('DB storage (MB)', readonly=True)
    server_id = fields.Many2one('saas_portal.server', string='Server', readonly=True)
    template_in_plan_ids = fields.One2many('saas_portal.plan', 'template_id', string='Template in Plans')
    state = fields.Selection([('template', 'Template'),
                              ('draft','New'),
                              ('open','In Progress'),
                              ('cancelled', 'Cancelled'),
                              ('pending','Pending'),
                              ('deleted','Deleted')],
                             'State', default='draft', track_visibility='onchange')

    expiration_datetime = fields.Datetime('Expiration', track_visibility='onchange')
    expired = fields.Boolean('Expiration', compute='_get_expired')
    last_connection = fields.Char(compute='_get_last_connection',
                                  string='Last Connection', size=64)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Record for this database already exists!'),
        ('client_id_uniq', 'unique (client_id)', 'client_id should be unique!'),
    ]

    @api.one
    def _get_last_connection(self):
        oat = self.pool.get('oauth.access_token')
        to_search = [('application_id', '=', self.id)]
        access_token_ids = oat.search(self.env.cr, self.env.uid, to_search)
        if access_token_ids:
            access_token = oat.browse(self.env.cr, self.env.uid,
                                      access_token_ids[0])
            self.last_connection = access_token.user_id.login_date

    @api.one
    def action_update_stats(self):
        self.server_id.action_update_stats()

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
    def delete_database_server(self):
        return self._delete_database_server()

    @api.one
    def _delete_database_server(self):
        state = {
            'd': self.name,
            'client_id': self.client_id,
        }
        url = self.server_id._request_server(path='/saas_server/delete_database', state=state, client_id=self.client_id)[0]
        res = requests.get(url)
        _logger.info('delete database: %s', res.text)
        if res.status_code != 500:
            self.state = 'deleted'

    @api.one
    def _get_expired(self):
        now = fields.Datetime.now()
        self.expired = self.expiration_datetime and self.expiration_datetime < now

    def delete_db(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'saas.config',
            'target': 'new',
            'context': {
                'default_action': 'delete',
                'default_server_id': obj.server_id.id,
                'default_database_id': obj.id,
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
        return super(OauthApplication, self).unlink(cr, uid, ids, context)


class ResUsers(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    plan_id = fields.Many2one('saas_portal.plan', 'Plan')
    organization = fields.Char('Organization', size=64)
    database = fields.Char('Database', size=64)
