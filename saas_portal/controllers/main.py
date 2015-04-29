# -*- coding: utf-8 -*-
import openerp
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.auth_oauth.controllers import main as oauth
import werkzeug
import simplejson
import uuid
import random


class SignupError(Exception):
    pass


class SaasPortal(http.Controller):

    @http.route(['/saas_portal/trial_check'], type='json', auth='public', website=True)
    def trial_check(self, **post):
        if self.exists_database(post['dbname']):
            return {"error": {"msg": "database already taken"}}
        return {"ok": 1}

    @http.route(['/saas_portal/book_then_signup'], type='http', auth='public', website=True)
    def book_then_signup(self, **post):
        full_dbname = self.get_full_dbname(post.get('dbname'))
        dbtemplate = self.get_template()
        # FIXME: line below should be deleted. This route called book_then_signup, but work as if user already signed up
        organization = self.update_user_and_partner(full_dbname)

        return self.create_new_database(dbtemplate, full_dbname, organization=organization)

    def create_demo_database(self, plan_id):
        cr, uid = request.cr, SUPERUSER_ID
        plan = request.registry['saas_portal.plan'].browse(cr, uid, [plan_id])
        full_dbname = plan.generate_dbname()[0]

        return self.create_new_database(plan.template, full_dbname, saas_server=plan.server_id)

    def create_new_database(self, dbtemplate, full_dbname, organization='YourCompany', saas_server=None):
        client_id = self.get_new_client_id(full_dbname)
        request.registry['oauth.application'].create(request.cr, SUPERUSER_ID, {'client_id': client_id, 'name':full_dbname})
        scheme = request.httprequest.scheme
        saas_server = saas_server or self.get_saas_server()

        params = {
            'scope': 'userinfo force_login trial skiptheuse',
            'state': simplejson.dumps({
                'd': full_dbname,
                'u': '%s://%s' % (scheme, full_dbname.replace('_', '.')),
                'o': organization, # FIXME: should be deleted. Organization name can be retrieved by saas_server via auth endpoint
                'db_template': dbtemplate,
            }),
            'redirect_uri': '{scheme}://{saas_server}/saas_server/new_database'.format(scheme=scheme, saas_server=saas_server.name),
            'response_type': 'token',
            'client_id': client_id,
        }
        return request.redirect('/oauth2/auth?%s' % werkzeug.url_encode(params))

    @http.route('/saas_portal/tenant', type='http', auth='public', website=True)
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
            return werkzeug.utils.redirect('/web')
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

    def get_provider(self):
        imd = request.registry['ir.model.data']
        return imd.xmlid_to_object(request.cr, SUPERUSER_ID,
                                   'saas_server.saas_oauth_provider')

    def get_new_client_id(self, name):
        return str(uuid.uuid1())

    def get_config_parameter(self, param):
        config = request.registry['ir.config_parameter']
        full_param = 'saas_portal.%s' % param
        return config.get_param(request.cr, SUPERUSER_ID, full_param)

    def get_full_dbname(self, dbname):
        full_dbname = '%s.%s' % (dbname, self.get_config_parameter('base_saas_domain'))
        return full_dbname.replace('www.', '').replace('.', '_')

    def get_saas_server(self):
        saas_server_list = request.env['saas_portal.server'].sudo().search([])
        return saas_server_list[random.randint(0, len(saas_server_list) - 1)]

    def exists_database(self, dbname):
        full_dbname = self.get_full_dbname(dbname)
        return openerp.service.db.exp_db_exist(full_dbname)

    def get_template(self):
        user_model = request.registry.get('res.users')
        user = user_model.browse(request.cr, SUPERUSER_ID, request.uid)
        if user.plan_id and user.plan_id.state == 'confirmed':
            return user.plan_id.template
        return self.get_config_parameter('dbtemplate')

    def update_user_and_partner(self, database):
        user_model = request.registry.get('res.users')
        user = user_model.browse(request.cr, SUPERUSER_ID, request.uid)
        partner_model = request.registry.get('res.partner')
        organization = user.organization or database.split('_')[0]
        wals = {
            'name': user.organization,
            'is_company': True,
            'country_id': user.country_id and user.country_id.id,
            'email': user.login
        }
        try:
            if hasattr(partner_model, user.plan_id.role_id.code):
                wals[user.plan_id.role_id.code] = True
        except:
            pass
        pid = partner_model.create(request.cr, SUPERUSER_ID, wals)
        vals = {
            'database': database,
            'email': user.login,
            'parent_id': pid
        }
        user_model.write(request.cr, SUPERUSER_ID, user.id, vals)
        return organization


class OAuthLogin(oauth.OAuthLogin):

    @http.route()
    def web_login(self, *args, **kw):
        if kw.get('login', False):
            user = request.registry.get('res.users')
            domain = [('login', '=', kw['login'])]
            fields = ['share', 'database']
            data = user.search_read(request.cr, SUPERUSER_ID, domain, fields)
            if data and data[0]['share'] and data[0]['database']:
                kw['redirect'] = '/saas_portal/tenant'
        return super(OAuthLogin, self).web_login(*args, **kw)

    @http.route()
    def web_auth_reset_password(self, *args, **kw):
        kw['reset'] = True
        if kw.get('login', False):
            user = request.registry.get('res.users')
            domain = [('login', '=', kw['login'])]
            fields = ['share', 'database']
            data = user.search_read(request.cr, SUPERUSER_ID, domain, fields)
            if data and data[0]['share'] and data[0]['database']:
                kw['redirect'] = '/saas_portal/tenant'
        return super(OAuthLogin, self).web_auth_reset_password(*args, **kw)
