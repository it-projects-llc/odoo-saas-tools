# -*- coding: utf-8 -*-
import openerp
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons import saas_portal_signup
from openerp.addons.saas_portal.controllers.main import SaasPortal


class AuthSignupHome(saas_portal_signup.controllers.main.AuthSignupHome):

    @http.route()
    def web_auth_signup(self, *args, **kw):
        if kw.get('dbname', False) and kw.get('product_id', False):
            redirect = '/saas_portal/add_new_client'
            kw['redirect'] = '%s?dbname=%s&product_id=%s&password=%s' % (
                redirect, kw['dbname'], kw['product_id'], kw['password'])
        return super(AuthSignupHome, self).web_auth_signup(*args, **kw)

    def get_auth_signup_qcontext(self):
        qcontext = super(AuthSignupHome, self).get_auth_signup_qcontext()

        if not qcontext.get('products', False):
            qcontext['products'] = request.env['product.template'].search([('plan_ids', '!=', False)])
        if not qcontext.get('sa_country_id', False):
            qcontext['sa_country_id'] = request.env.ref('base.sa').id

        return qcontext


class AuthSaasPortal(SaasPortal):

    @http.route()
    def add_new_client(self, **post):

        product = request.env['product.template'].browse(int(post.get('product_id')))
        dbnames = []
        if product and product.plan_ids:
            for plan in product.plan_ids:

                kw = post.copy()
                kw['dbname'] = plan.dbname_prefix and plan.dbname_prefix + post.get('dbname') \
                    or post.get('dbname')
                kw['plan_id'] = plan.id
                dbname = self.get_full_dbname(kw['dbname'])
                res = super(AuthSaasPortal, self).add_new_client(**kw)
                dbnames.append(dbname)

            template = product.on_create_email_template
            if template:
                email_ctx = {
                    'default_model': 'product.template',
                    'default_res_id': product.id,
                    'default_use_template': bool(template),
                    'default_template_id': template.id,
                    'default_composition_mode': 'comment',
                    'dbnames': dbnames,
                    'from_user': request.env['res.users'].sudo().browse(SUPERUSER_ID),
                    'partner_to': request.env['res.users'].sudo().browse(request.session.uid).partner_id.id,
                }
                composer = request.env['mail.compose.message'].sudo().with_context(email_ctx).create({})
                composer.send_mail()

            return res
