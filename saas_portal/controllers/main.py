# -*- coding: utf-8 -*-
from urllib import urlencode
from ast import literal_eval
import odoo
from odoo import SUPERUSER_ID, exceptions
from odoo.tools.translate import _
from odoo import http
from odoo.http import request
from odoo.addons.saas_base.exceptions import MaximumDBException, MaximumTrialDBException
import werkzeug
import simplejson
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SignupError(Exception):
    pass


class SaasPortal(http.Controller):

    @http.route(['/saas_portal/trial_check'], type='json', auth='public', website=True)
    def trial_check(self, **post):
        if self.exists_database(post['dbname']):
            return {"error": {"msg": "database already taken"}}
        return {"ok": 1}

    @http.route(['/saas_portal/add_new_client'], type='http', auth='public', website=True)
    def add_new_client(self, redirect_to_signup=False, **post):
        uid = request.session.uid
        if not uid:
            url = '/web/signup' if redirect_to_signup else '/web/login'
            redirect = unicode('/saas_portal/add_new_client?' + urlencode(post))
            query = {'redirect': redirect}
            return http.local_redirect(path=url, query=query)

        dbname = self.get_full_dbname(post.get('dbname'))
        user_id = request.session.uid
        partner_id = None
        if user_id:
            user = request.env['res.users'].browse(user_id)
            partner_id = user.partner_id.id
        plan = self.get_plan(int(post.get('plan_id', 0) or 0))
        trial = bool(post.get('trial'))
        try:
            res = plan.create_new_database(dbname=dbname,
                                           user_id=user_id,
                                           partner_id=partner_id,
                                           trial=trial,)
        except MaximumDBException:
            url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_maximumdb', '/')
            return werkzeug.utils.redirect(url)
        except MaximumTrialDBException:
            url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_maximumtrialdb', '/')
            return werkzeug.utils.redirect(url)

        return werkzeug.utils.redirect(res.get('url'))

    @http.route(['/saas_portal/rename_client'], type='http', auth='user', website=True)
    def rename_client(self, **post):
        client_id = int(post.get('client_id'))
        new_domain_name = post.get('dbname')
        user_id = request.session.uid
        user = request.env['res.users'].browse(user_id)

        client_obj = request.env['saas_portal.client'].sudo().browse(client_id)
        client_obj.check_partner_access(user.partner_id.id)

        client_obj.sudo().rename_database(new_domain_name)
        config_obj = request.env['ir.config_parameter']
        url = config_obj.sudo().get_param('web.base.url') + '/my/home'
        return werkzeug.utils.redirect(url)

    def get_config_parameter(self, param):
        config = request.env['ir.config_parameter']
        full_param = 'saas_portal.%s' % param
        return config.get_param(full_param)

    def get_full_dbname(self, dbname):
        if not dbname:
            return None
        full_dbname = '%s.%s' % (dbname, self.get_config_parameter('base_saas_domain'))
        return full_dbname.replace('www.', '')

    def get_plan(self, plan_id=None):
        plan_obj = request.env['saas_portal.plan']
        if not plan_id:
            domain = [('state', '=', 'confirmed')]
            plans = request.env['saas_portal.plan'].search(domain)
            if plans:
                return plans[0]
            else:
                raise exceptions.Warning(_('There is no plan configured'))
        return plan_obj.sudo().browse(plan_id)

    def exists_database(self, dbname):
        full_dbname = self.get_full_dbname(dbname)
        return odoo.service.db.exp_db_exist(full_dbname)

    @http.route(['/publisher-warranty/'], type='http', auth='public', website=True)
    def publisher_warranty(self, **post):
        # check addons/mail/update.py::_get_message for arg0 value
        arg0 = post.get('arg0')
        if arg0:
            arg0 = literal_eval(arg0)
        messages = []
        return simplejson.dumps({'messages': messages})
