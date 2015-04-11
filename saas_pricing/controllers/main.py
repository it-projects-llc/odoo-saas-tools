# -*- coding: utf-8 -*-
import openerp
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.auth_oauth.controllers import main as oauth
from openerp.addons.auth_signup.controllers import main as signup
import werkzeug
import simplejson
import uuid
import random


class SignupError(Exception):
    pass


class SaasPortal(http.Controller):

    @http.route('/saas_portal/signup', type='http', auth="none", website=True)
    def web_portal_signup(self, redirect="/saas_portal/book_then_signup", **kw):
        dbname = request.params['dbname']
        if self.exists_database(dbname):
            full_dbname = self.get_full_dbname(dbname)
            params = {'db': full_dbname, 'login': 'admin', 'key': 'admin'}
            redirect = 'http://%s/login' % full_dbname.replace('_', '.')
        else:
            params = request.params
            auth_signup = signup.AuthSignupHome()
            qcontext = auth_signup.get_auth_signup_qcontext()
            auth_signup.do_signup(qcontext)
            params['uid'] = request.uid
        return request.redirect('%s?%s' % (redirect, werkzeug.url_encode(params)))

    @http.route(['/saas_portal/trial_check'], type='json', auth='public', website=True)
    def trial_check(self, **post):
        if self.exists_database(post['dbname']):
            return {"error": {"msg": "database already taken"}}
        return {"ok": 1}

    @http.route(['/saas_portal/book_then_signup'], type='http', auth='public', website=True)
    def book_then_signup(self, **post):
        saas_server = self.get_saas_server()
        scheme = request.httprequest.scheme
        full_dbname = self.get_full_dbname(post.get('dbname'))
        dbtemplate = self.get_config_parameter('dbtemplate')
        client_id = self.get_new_client_id(full_dbname)
        request.registry['oauth.application'].create(request.cr, SUPERUSER_ID, {'client_id': client_id, 'name':full_dbname})
        params = {
            'scope': 'userinfo force_login trial skiptheuse',
            'state': simplejson.dumps({
                'd': full_dbname,
                'u': '%s://%s' % (scheme, full_dbname.replace('_', '.')),
                'db_template': dbtemplate,
            }),
            'redirect_uri': '{scheme}://{saas_server}/saas_server/new_database'.format(scheme=scheme, saas_server=saas_server),
            'response_type': 'token',
            'organization': post.get('organization'),
            'client_id': client_id,
        }
        return request.redirect('/oauth2/auth?%s' % werkzeug.url_encode(params))

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
        saas_server_list = self.get_config_parameter('saas_server_list')
        saas_server_list = saas_server_list.split(',')
        return saas_server_list[random.randint(0, len(saas_server_list) - 1)]

    def exists_database(self, dbname):
        full_dbname = self.get_full_dbname(dbname)
        return openerp.service.db.exp_db_exist(full_dbname)


class OAuthLogin(oauth.OAuthLogin):

    @http.route()
    def web_login(self, *args, **kw):
        if kw.get('login', False):
            user = request.registry.get('res.users')
            domain = [('login', '=', kw['login'])]
            fields = ['share', 'database']
            data = user.search_read(request.cr, SUPERUSER_ID, domain, fields)
            if data and data[0]['share'] and data[0]['database']:
                kw['redirect'] = '/saas_server/tenant'
        return super(OAuthLogin, self).web_login(*args, **kw)

    @http.route()
    def web_auth_signup(self, *args, **kw):
        if kw.get('dbname', False):
            redirect = '/saas_portal/book_then_signup'
            kw['redirect'] = '%s?dbname=%s' % (redirect, kw['dbname'])
        return super(OAuthLogin, self).web_auth_signup(*args, **kw)
