# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api, SUPERUSER_ID, exceptions
from openerp.addons.saas_utils import connector, database
from openerp import http
from openerp.tools import config
from openerp.tools.translate import _
import time
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

    name = fields.Char('Database Name')
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
    def _request(self, add_host=False, **kw):
        params = self._request_params(**kw)[0]
        url = '/oauth2/auth?%s' % werkzeug.url_encode(params)
        if add_host:
            domain = self.env['ir.config_parameter'].get_param('saas_portal.base_saas_domain')
            scheme = 'http'
            url = '{scheme}://{domain}{url}'.format(scheme=scheme, domain=domain, url=url)
        return url

    @api.one
    def _request_server(self, **kw):
        # TODO: get access_token manually and make redirection
        params = self._request_params(**kw)[0]

    @api.model
    def action_update_stats_all(self):
        self.search([]).action_update_stats()

    @api.one
    def action_update_stats(self):
        scheme = 'https' if self.https else 'http'
        url = '{scheme}://{domain}/saas_server/stats'.format(scheme=scheme, domain=self.name)
        data = urllib2.urlopen(url).read()
        data = simplejson.loads(data)
        print 'data', data
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


class SaasPortalPlan(models.Model):
    _name = 'saas_portal.plan'

    name = fields.Char('Plan', required=True)
    template_id = fields.Many2one('oauth.application', 'Template DB', required=True)
    demo = fields.Boolean('Install Demo Data')

    def _get_default_lang_id(self):
        lang = self.env['res.lang'].search([('code', '=', self.env.lang)])
        return lang and lang[0]
    lang_id = fields.Many2one('res.lang', 'Language', default=_get_default_lang_id)
    sequence = fields.Integer('Sequence')
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')],
                             'State', default='draft', compute='_get_state', store=True)
    role_id = fields.Many2one('saas_server.role', 'Role')
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
    server_id = fields.Many2one('saas_portal.server', string='SaaS Server', help='Force apply this saas server', states={'draft':[('readonly', False)]}, readonly=True, required=True)


    @api.one
    @api.depends('template_id.state')
    def _get_state(self):
        if self.template_id.state == 'template':
            self.state = 'confirmed'
        elif self.template_id.state == 'deleted':
            self.state = 'draft'


    @api.one
    def generate_dbname(self):
        # TODO make more elegant solution
        return self.dbname_template.replace('%i', str(random.randint(100, 10000)))

    @api.multi
    def create_template(self):
        assert len(self)==1, 'This method is applied only for single record'
        plan = self[0]
        addons = [x.name for x in plan.required_addons_ids]
        state = {
            'd': plan.template_id.name,
            'demo': plan.demo and 1 or 0,
            'addons': addons,
            'lang': plan.lang_id.code,
            'is_template_db': 1,
        }
        url = plan.server_id._request(path='/saas_server/new_database', state=state)
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'name': 'Create Template',
            'url': url
        }

    @api.multi
    def edit_template(self):
        return self[0].template_id.edit_db()

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
        #self.template_id._delete_db()

        #tmp solution:
        state = {
            'd': self.template_id.name,
            'client_id': self.template_id.client_id,
        }
        url = self.server_id._request(path='/saas_server/delete_database', state=state)[0]
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'name': 'Delete Template',
            'url': url
        }



class SaasServerRole(models.Model):
    _name = 'saas_server.role'

    name = fields.Char('Name', size=64)
    code = fields.Char('Code', size=64)


class OauthApplication(models.Model):
    _name = 'oauth.application'
    _description = 'Client'

    _inherit = ['oauth.application', 'mail.thread']

    name = fields.Char('Database name', readonly=False)
    client_id = fields.Char('Client ID', readonly=True, select=True)
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
    
    expiration = fields.Datetime('Expiration', track_visibility='onchange')
    expired = fields.Boolean('Expiration', compute='_get_expired')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Record for this database already exists!'),
        ('client_id_uniq', 'unique (client_id)', 'client_id should be unique!'),
    ]

    @api.model
    def generate_client_id(self):
        return str(uuid.uuid1())

    @api.model
    def delete_expired_databases(self):
        now = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.search([('expiration', '<=', now)])._delete_db()

    @api.one
    def _delete_db(self):
        state = {
            'd': self.name
        }
        req = self.server_id._request_server(path='/saas_server/delete_database', state=state)[0]
        res = requests.get(req)
        _logger.info('delete database: %s', res.text)
        self.state = 'deleted'

    @api.one
    def _get_expired(self):
        now = fields.Datetime.now()
        self.expired = self.expiration and self.expiration < now

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
                'default_database': obj.name,
                'default_server_id': obj.server_id.id
            }
        }

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
                'default_server_id': obj.server_id.id,
                'default_database_id': obj.id,
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
