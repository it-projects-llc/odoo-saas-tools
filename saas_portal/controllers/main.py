# -*- coding: utf-8 -*-
from ast import literal_eval
import openerp
from openerp import SUPERUSER_ID, exceptions
from openerp.tools.translate import _
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.auth_oauth.controllers import main as oauth
import werkzeug
import simplejson


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
        dbname = self.get_full_dbname(post.get('dbname'))
        plan = self.get_default_plan()
        url = plan._create_new_database(dbname)[0]
        return werkzeug.utils.redirect(url)

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

    def get_config_parameter(self, param):
        config = request.registry['ir.config_parameter']
        full_param = 'saas_portal.%s' % param
        return config.get_param(request.cr, SUPERUSER_ID, full_param)

    def get_full_dbname(self, dbname):
        full_dbname = '%s.%s' % (dbname, self.get_config_parameter('base_saas_domain'))
        return full_dbname.replace('www.', '')

    def get_default_plan(self):
        # TODO: how we identify a default plan?
        plan = request.registry['saas_portal.plan']
        plan_ids = request.registry['saas_portal.plan'].search(request.cr, SUPERUSER_ID, [('state', '=', 'confirmed')])
        if not plan_ids:
            raise exceptions.Warning(_('There is no plan configured'))
        return plan.browse(request.cr, SUPERUSER_ID, plan_ids[0])

    def exists_database(self, dbname):
        full_dbname = self.get_full_dbname(dbname)
        return openerp.service.db.exp_db_exist(full_dbname)

    @http.route(['/publisher-warranty/'], type='http', auth='public', website=True)
    def publisher_warranty(self, **post):
        # check addons/mail/update.py::_get_message for arg0 value
        arg0 = post.get('arg0')
        if arg0:
            arg0 = literal_eval(arg0)
        messages = []
        return simplejson.dumps({'messages':messages})


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
        if kw.get('login', False):
            user = request.registry.get('res.users')
            domain = [('login', '=', kw['login'])]
            fields = ['share', 'database']
            data = user.search_read(request.cr, SUPERUSER_ID, domain, fields)
            if data and data[0]['share'] and data[0]['database']:
                kw['redirect'] = '/saas_portal/tenant'
        return super(OAuthLogin, self).web_auth_reset_password(*args, **kw)
