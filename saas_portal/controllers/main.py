# -*- coding: utf-8 -*-
import openerp
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.auth_oauth.controllers import main as oauth
from openerp.addons import auth_signup
import werkzeug
import simplejson
import uuid
import random
import re


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
        saas_server = self.get_saas_server()
        scheme = request.httprequest.scheme
        full_dbname = self.get_full_dbname(post.get('dbname'))
        dbtemplate = self.get_template()
        client_id = self.get_new_client_id(full_dbname)
        request.registry['oauth.application'].create(request.cr, SUPERUSER_ID, {'client_id': client_id, 'name':full_dbname})
        user = self.update_user_and_partner(full_dbname)
        params = {
            'scope': 'userinfo force_login trial skiptheuse',
            'state': simplejson.dumps({
                'd': full_dbname,
                'u': '%s://%s' % (scheme, full_dbname.replace('_', '.')),
                'o': user.organization,
                'db_template': dbtemplate,
            }),
            'redirect_uri': '{scheme}://{saas_server}/saas_server/new_database'.format(scheme=scheme, saas_server=saas_server),
            'response_type': 'token',
            'organization': post.get('organization'),
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
        saas_server_list = self.get_config_parameter('saas_server_list')
        saas_server_list = saas_server_list.split(',')
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
        return user


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

    @http.route()
    def web_auth_reset_password(self, *args, **kw):
        kw['reset'] = True
        if kw.get('login', False):
            user = request.registry.get('res.users')
            domain = [('login', '=', kw['login'])]
            fields = ['share', 'database']
            data = user.search_read(request.cr, SUPERUSER_ID, domain, fields)
            if data and data[0]['share'] and data[0]['database']:
                kw['redirect'] = '/saas_server/tenant'
        return super(OAuthLogin, self).web_auth_reset_password(*args, **kw)


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
            assert re.match('[a-zA-Z0-9_.-]+$', qcontext.get('dbname')), "Only letters or numbers are allowed in domain."
            assert db_exists == False, "Domain exists"
        assert any([k for k in values.values()]), "The form was not properly filled in."
        assert values.get('password') == qcontext.get('confirm_password'), "Passwords do not match; please retype them."
        assert qcontext.get('organization') != qcontext.get('name'), "Name and Organization must be different."
        self._signup_with_values(qcontext.get('token'), values)
        request.cr.commit()
