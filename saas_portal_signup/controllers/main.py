# -*- coding: utf-8 -*-
import openerp
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.auth_oauth.controllers import main as oauth
from openerp.addons import auth_signup
import re


class OAuthLogin(oauth.OAuthLogin):

    @http.route()
    def web_auth_signup(self, *args, **kw):
        if kw.get('dbname', False):
            redirect = '/saas_portal/book_then_signup'
            kw['redirect'] = '%s?dbname=%s' % (redirect, kw['dbname'])
        return super(OAuthLogin, self).web_auth_signup(*args, **kw)


class AuthSignupHome(auth_signup.controllers.main.AuthSignupHome):

    def get_auth_signup_qcontext(self):
        qcontext = super(AuthSignupHome, self).get_auth_signup_qcontext()
        context = request.context
        if qcontext.get('token', False):
            qcontext['reset'] = True
        if not qcontext.get('plans', False):
            sp = request.registry.get('saas_portal.plan')
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
        assert re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", values['email']), "Please enter a valid email address."
        assert any([k for k in values.values()]), "The form was not properly filled in."
        assert values.get('password') == qcontext.get('confirm_password'), "Passwords do not match; please retype them."
        assert qcontext.get('organization') != qcontext.get('name'), "Name and Organization must be different."
        self._signup_with_values(qcontext.get('token'), values)
        request.cr.commit()
