# -*- coding: utf-8 -*-
import openerp
from openerp import SUPERUSER_ID
from openerp import http
from openerp.addons import auth_signup
from openerp.addons.web.http import request
from openerp.addons.auth_oauth.controllers.main import fragment_to_query_string
from openerp.addons.web.controllers.main import db_monodb
from openerp.addons.saas_utils import connector
import re

import werkzeug.utils
import simplejson


import logging
_logger = logging.getLogger(__name__)


class SaasServer(http.Controller):

    @http.route('/saas_server/new_database', type='http', auth='public')
    @fragment_to_query_string
    def new_database(self, **post):
        _logger.info('new_database post: %s', post)

        state = simplejson.loads(post.get('state'))
        new_db = state.get('d')
        template_db = self.get_template(state)
        action = 'base.open_module_tree'
        access_token = post['access_token']
        saas_oauth_provider = request.registry['ir.model.data'].xmlid_to_object(request.cr, SUPERUSER_ID, 'saas_server.saas_oauth_provider')

        admin_data = request.registry['res.users']._auth_oauth_rpc(request.cr, SUPERUSER_ID, saas_oauth_provider.validation_endpoint, access_token)
        if admin_data.get("error"):
            raise Exception(admin_data['error'])
        client_id = admin_data.get('client_id')

        user = self.update_user_and_partner(new_db)
        organization = user.organization
        country_id = user.country_id and user.country_id.id

        openerp.service.db._drop_conn(request.cr, template_db)
        openerp.service.db.exp_drop(new_db) # for debug
        openerp.service.db.exp_duplicate_database(template_db, new_db)

        registry = openerp.modules.registry.RegistryManager.get(new_db)

        with registry.cursor() as cr:
            # update database.uuid
            registry['ir.config_parameter'].set_param(cr, SUPERUSER_ID,
                                                      'database.uuid',
                                                      client_id)
            # save auth data
            oauth_provider_data = {'enabled': True, 'client_id': client_id}
            for attr in ['name', 'auth_endpoint', 'scope', 'validation_endpoint', 'data_endpoint', 'css_class', 'body']:
                oauth_provider_data[attr] = getattr(saas_oauth_provider, attr)
            oauth_provider_id = registry['auth.oauth.provider'].create(cr, SUPERUSER_ID, oauth_provider_data)
            registry['ir.model.data'].create(cr, SUPERUSER_ID, {
                'name': 'saas_oauth_provider',
                'module': 'saas_server',
                'noupdate': True,
                'model': 'auth.oauth.provider',
                'res_id': oauth_provider_id,
            })
            # 1. Update company with organization
            vals = {'name': organization, 'country_id': country_id}
            registry['res.company'].write(cr, SUPERUSER_ID, 1, vals)
            partner = registry['res.company'].browse(cr, SUPERUSER_ID, 1)
            registry['res.partner'].write(cr, SUPERUSER_ID, partner.id,
                                          {'email': admin_data['email']})
            # 2. Update user credentials
            domain = [('login', '=', template_db)]
            user_ids = registry['res.users'].search(cr, SUPERUSER_ID, domain)
            user_id = user_ids and user_ids[0] or SUPERUSER_ID
            user = registry['res.users'].browse(cr, SUPERUSER_ID, user_id)
            user.write({
                'login': admin_data['email'],
                'name': admin_data['name'],
                'email': admin_data['email'],
                'country_id': country_id,
                'parent_id': partner.id,
                'oauth_provider_id': oauth_provider_id,
                'oauth_uid': admin_data['user_id'],
                'oauth_access_token': access_token
            })
            # 3. Set suffix for all sequences
            seq_ids = registry['ir.sequence'].search(cr, SUPERUSER_ID,
                                                     [('suffix', '=', False)])
            suffix = {'suffix': client_id.split('-')[0]}
            registry['ir.sequence'].write(cr, SUPERUSER_ID, seq_ids, suffix)
            # get action_id
            action_id = registry['ir.model.data'].xmlid_to_res_id(cr, SUPERUSER_ID, action)

        params = {
            'access_token': post['access_token'],
            'state': simplejson.dumps({
                'd': new_db,
                'p': oauth_provider_id,
                'a': action_id
                }),
            'action': action
            }
        scheme = request.httprequest.scheme
        return werkzeug.utils.redirect('{scheme}://{domain}/saas_client/new_database?{params}'.format(scheme=scheme, domain=new_db.replace('_', '.'), params=werkzeug.url_encode(params)))

    @http.route(['/saas_server/stats'], type='http', auth='public')
    def stats(self, **post):
        # TODO auth
        server_db = db_monodb()
        res = request.registry['saas_server.client'].update_all(request.cr, SUPERUSER_ID, server_db)
        return simplejson.dumps(res)

    @http.route('/saas_server/tenant', type='http', auth='public', website=True)
    def tenant(self, **post):
        if request.uid == SUPERUSER_ID:
            return werkzeug.utils.redirect('/web')
        user = request.registry.get('res.users').browse(request.cr,
                                                        SUPERUSER_ID,
                                                        request.uid)
        db = user.database
        registry = openerp.modules.registry.RegistryManager.get(db)
        with registry.cursor() as cr:
            to_search = [('login', '=', user.login)]
            fields = ['oauth_provider_id', 'oauth_access_token']
            data = registry['res.users'].search_read(cr, SUPERUSER_ID,
                                                     to_search, fields)
        if not data:
            raise Exception("Missing User!!!")
        params = {
            'access_token': data[0]['oauth_access_token'],
            'state': simplejson.dumps({
                'd': db,
                'p': data[0]['oauth_provider_id'][0]
            }),
        }
        scheme = request.httprequest.scheme
        domain = db.replace('_', '.')
        params = werkzeug.url_encode(params)
        return werkzeug.utils.redirect('{scheme}://{domain}/auth_oauth/signin?{params}'.format(scheme=scheme, domain=domain, params=params))

    def get_template(self, state):
        user_model = request.registry.get('res.users')
        user = user_model.browse(request.cr, SUPERUSER_ID, request.uid)
        if user.plan_id and user.plan_id.state == 'confirmed':
            return user.plan_id.template
        return state.get('db_template')

    def update_user_and_partner(self, database):
        user_model = request.registry.get('res.users')
        user = user_model.browse(request.cr, SUPERUSER_ID, request.uid)
        partner_model = request.registry.get('res.partner')
        wals = {
            'name': user.organization,
            'is_company': True,
            'country_id': user.country_id and user.country_id.id,
            'email': user.login
        }
        pid = partner_model.create(request.cr, SUPERUSER_ID, wals)
        vals = {
            'database': database,
            'email': user.login,
            'parent_id': pid
        }
        user_model.write(request.cr, SUPERUSER_ID, user.id, vals)
        return user


class AuthSignupHome(auth_signup.controllers.main.AuthSignupHome):

    def get_auth_signup_qcontext(self):
        qcontext = super(AuthSignupHome, self).get_auth_signup_qcontext()
        context = request.context
        if not qcontext.get('plans', False):
            sp = request.registry.get('saas_server.plan')
            plan_ids = sp.search(request.cr, SUPERUSER_ID, [], context=context)
            qcontext['plans'] = sp.browse(request.cr, SUPERUSER_ID, plan_ids, context=context)
        if not qcontext.get('countries', False):
            orm_country = request.registry.get('res.country')
            country_ids = orm_country.search(request.cr, SUPERUSER_ID, [], context=context)
            countries = orm_country.browse(request.cr, SUPERUSER_ID, country_ids, context=context)
            qcontext['countries'] = countries
        if not qcontext.get('base_saas_domain', False):
            qcontext['base_saas_domain'] = self.get_saas_domain()
        return qcontext

    def get_saas_domain(self):
        config = request.registry['ir.config_parameter']
        full_param = 'saas_portal.base_saas_domain'
        base_saas_domain = config.get_param(request.cr, SUPERUSER_ID, full_param)
        return base_saas_domain

    def do_signup(self, qcontext):
        values = dict((key, qcontext.get(key)) for key in ('login', 'name', 'password'))
        values['email'] = qcontext['login']
        if qcontext.get('plan_id', False):
            values['plan_id'] = qcontext['plan_id']
        if qcontext.get('organization', False):
            values['organization'] = qcontext['organization']
        if qcontext.get('country_id', False):
            values['country_id'] = qcontext['country_id']
        if qcontext.get('dbname', False):
            f_dbname = '%s.%s' % (qcontext['dbname'], self.get_saas_domain())
            full_dbname = f_dbname.replace('www.', '').replace('.', '_')
            db_exists = openerp.service.db.exp_db_exist(full_dbname)
            assert db_exists == False, "Domain exists"
        assert any([k for k in values.values()]), "The form was not properly filled in."
        assert values.get('password') == qcontext.get('confirm_password'), "Passwords do not match; please retype them."
        self._signup_with_values(qcontext.get('token'), values)
        request.cr.commit()
