# -*- coding: utf-8 -*-
import openerp
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons import saas_portal_signup
from openerp.addons.saas_portal.controllers.main import SaasPortal


class AuthSignupHome(saas_portal_signup.controllers.main.AuthSignupHome):

    @http.route()
    def web_auth_signup(self, *args, **kw):
        if kw.get('dbname', False) and kw.get('product_id', False):
            redirect = '/saas_portal/add_new_client'
            kw['redirect'] = '%s?dbname=%s&product_id=%s' % (
                redirect, kw['dbname'], kw['product_id'])
        return super(AuthSignupHome, self).web_auth_signup(*args, **kw)

    def get_auth_signup_qcontext(self):
        qcontext = super(AuthSignupHome, self).get_auth_signup_qcontext()

        if not qcontext.get('products', False):
            qcontext['products'] = request.env['product.template'].search([('saas_template_id', '!=', False)])

        return qcontext


class AuthSaasPortal(SaasPortal):

    @http.route()
    def add_new_client(self, **post):

        product = request.env['product.template'].browse(int(post.get('product_id')))
        if product and product.plan_ids:
            for plan in product.plan_ids:

                kw = post.copy()
                kw['dbname'] = plan.dbname_prefix and plan.dbname_prefix + post.get('dbname') \
                    or post.get('dbname')
                kw['plan_id'] = plan.id
                res = super(AuthSaasPortal, self).add_new_client(**kw)
            return res
