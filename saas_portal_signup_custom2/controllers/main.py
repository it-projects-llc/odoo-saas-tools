# -*- coding: utf-8 -*-

import werkzeug
from odoo import http
import re
from odoo.http import request
import logging

import odoo
from odoo import SUPERUSER_ID
from odoo.tools.translate import _
from odoo.addons import auth_signup
from odoo.addons.saas_portal.controllers.main import SaasPortal
from odoo.addons.website_payment.controllers.main import WebsitePayment
from odoo.addons.auth_signup.models.res_users import SignupError

_logger = logging.getLogger(__name__)

class AuthSignupHome(auth_signup.controllers.main.AuthSignupHome):

    @http.route()
    def web_auth_signup(self, *args, **kw):

        qcontext = self.get_auth_signup_qcontext()
        qcontext['error'] = _("Incorrect. Try again")
        if kw.has_key('g-recaptcha-response') and not request.website.recaptcha_siteverify(kw.get('g-recaptcha-response')):
            return request.render('auth_signup.signup', qcontext)

        if kw.get('dbname', False) and kw.get('product_id', False):
            redirect = '/saas_portal/add_new_client'
            kw['redirect'] = '%s?dbname=%s&product_id=%s&password=%s&trial_or_working=%s' % (
                redirect, kw['dbname'], kw['product_id'], kw['password'], kw['trial_or_working'])

        # return super(AuthSignupHome, self).web_auth_signup(*args, **kw)
# imp parent code: instead of showing ``Could not create a new account`` show assertion error text (e.g. if the passwords don't match)
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                return super(AuthSignupHome, self).web_login(*args, **kw)
            except (SignupError, AssertionError), e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error(e.message)
                    qcontext['error'] = e.message

        return request.render('auth_signup.signup', qcontext)
# end parent code

    def get_auth_signup_qcontext(self):
        qcontext = super(AuthSignupHome, self).get_auth_signup_qcontext()
        if not qcontext.get('countries', False):
            qcontext['countries'] = request.env['res.country'].search([])
        if not qcontext.get('base_saas_domain', False):
            qcontext['base_saas_domain'] = self.get_saas_domain()
        if not qcontext.get('products', False):
            qcontext['products'] = request.env['product.template'].sudo().search([('plan_ids', '!=', False)])
        return qcontext

    def get_saas_domain(self):
        config = request.env['ir.config_parameter']
        full_param = 'saas_portal.base_saas_domain'
        base_saas_domain = config.get_param(full_param)
        return base_saas_domain

    def do_signup(self, qcontext):
        values = dict((key, qcontext.get(key)) for key in ('login', 'name', 'password'))
        values['email'] = qcontext['login']
        if qcontext.get('country_id', False):
            values['country_id'] = qcontext['country_id']
        if qcontext.get('dbname', False):
            f_dbname = '%s.%s' % (qcontext['dbname'], self.get_saas_domain())
            full_dbname = f_dbname.replace('www.', '')
            db_exists = odoo.service.db.exp_db_exist(full_dbname)
            assert re.match('[a-zA-Z0-9_.-]+$', qcontext.get('dbname')), "Only letters or numbers are allowed in domain."
            assert db_exists == False, "Domain exists"
        assert re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", values['email']), "Please enter a valid email address."
        assert any([k for k in values.values()]), "The form was not properly filled in."
        assert values.get('password') == qcontext.get('confirm_password'), "Passwords do not match; please retype them."
        self._signup_with_values(qcontext.get('token'), values)
        request.cr.commit()


class AuthSaasPortal(SaasPortal):

    @http.route()
    def add_new_client(self, **post):

        product = request.env['product.template'].sudo().browse(int(post.get('product_id')))
        dbnames = []
        if product and product.plan_ids:
            for plan in product.plan_ids:

                kw = post.copy()
                kw['dbname'] = plan.dbname_prefix and plan.dbname_prefix + post.get('dbname') \
                    or post.get('dbname')
                kw['plan_id'] = plan.id
                kw['trial'] = kw['trial_or_working'] == 'trial'
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
                product.with_context(email_ctx).message_post_with_template(template.id, composition_mode='comment')

            return res


class SaaSWebsitePayment(WebsitePayment):

    @http.route()
    def pay(self, reference='', amount=False, currency_id=None, acquirer_id=None, **kw):
        return super(SaaSWebsitePayment, self).pay(reference=reference,
                                                   amount=amount,
                                                   currency_id=currency_id,
                                                   acquirer_id=acquirer_id, **kw)

    @http.route(['/saas_payment/pay'], type='http', auth='public', website=True)
    def saas_pay(self, **kw):
        contract_id = kw.get('contract_id')
        if contract_id:
            contract = request.env['account.analytic.account'].browse(contract_id)
            saas_portal_client = request.env['saas_portal.client'].sudo().search([('contract_id', '=', int(contract_id))], limit=1)
            if saas_portal_client.trial:
                if kw.get('convert_or_new') == 'convert':
                    saas_portal_client.trial = False
                elif kw.get('convert_or_new') == 'new':
                    name = saas_portal_client.name
                    plan = saas_portal_client.plan_id
                    partner_id = saas_portal_client.partner_id.id
                    user_id = request.session.uid
                    contract_id = saas_portal_client.contract_id

                    saas_portal_client.delete_database_server()

                    res = plan._create_new_database(dbname=name,
                                                    partner_id=partner_id,
                                                    user_id=user_id)
                    saas_portal_client = request.env['saas_portal.client'].sudo().browse(res['id'])
                    saas_portal_client.contract_id = contract_id
                else:
                    return request.render('saas_portal_signup_custom2.saas_trial_pay')

        url = '/website_payment/pay?%s' % werkzeug.url_encode(kw)
        return request.redirect(url)
