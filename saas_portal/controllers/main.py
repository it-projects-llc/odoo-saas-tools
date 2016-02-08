# -*- coding: utf-8 -*-
from ast import literal_eval
import openerp
from openerp import SUPERUSER_ID, exceptions
from openerp.tools.translate import _
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.saas_base.exceptions import MaximumDBException, MaximumTrialDBException
import werkzeug
import simplejson
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SignupError(Exception):
    pass


class SaasPortal(http.Controller):

    @http.route(['/saas_portal/trial_check'], type='json', auth='public', website=True)
    def trial_check(self, **post):
        if self.exists_database(post['dbname']):
            return {"error": {"msg": "database already taken"}}
        return {"ok": 1}

    @http.route(['/saas_portal/add_new_client'], type='http', auth='user', website=True)
    def add_new_client(self, **post):
        dbname = self.get_full_dbname(post.get('dbname'))
        user_id = request.session.uid
        partner_id = None
        if user_id:
            user = request.env['res.users'].browse(user_id)
            partner_id = user.partner_id.id
        plan = self.get_plan(int(post.get('plan_id', 0) or 0))
        try:
            res = plan.create_new_database(dbname=dbname, user_id=user_id, partner_id=partner_id)
        except MaximumDBException:
            url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_maximumdb', '/')
            return werkzeug.utils.redirect(url)
        except MaximumTrialDBException:
            url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_maximumtrialdb', '/')
            return werkzeug.utils.redirect(url)

        return werkzeug.utils.redirect(res.get('url'))

    def get_config_parameter(self, param):
        config = request.registry['ir.config_parameter']
        full_param = 'saas_portal.%s' % param
        return config.get_param(request.cr, SUPERUSER_ID, full_param)

    def get_full_dbname(self, dbname):
        if not dbname:
            return None
        full_dbname = '%s.%s' % (dbname, self.get_config_parameter('base_saas_domain'))
        return full_dbname.replace('www.', '')

    def get_plan(self, plan_id=None):
        plan = request.registry['saas_portal.plan']
        if not plan_id:
            domain = [('state', '=', 'confirmed')]
            plan_ids = request.registry['saas_portal.plan'].search(request.cr, SUPERUSER_ID, domain)
            if plan_ids:
                plan_id = plan_ids[0]
            else:
                raise exceptions.Warning(_('There is no plan configured'))
        return plan.browse(request.cr, SUPERUSER_ID, plan_id)

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


class SaasPortalSale(http.Controller):
    @http.route('/trial', auth='public', type='http', website=True)
    def index(self, **kw):
        uid = request.session.uid
        plan_id = int(kw.get('plan_id'))
        if not uid:
            url = '/web/login?redirect=/trial'
            query = {'plan_id': str(plan_id)}
            return http.local_redirect(path=url, query=query)

        partner = request.env['res.users'].browse(uid).partner_id
        trial_plan = request.env['saas_portal.plan'].sudo().browse(plan_id)
        support_team = request.env.ref('saas_portal.main_support_team')

        try:
            trial_plan.create_new_database(partner_id=partner.id, user_id=uid, notify_user=True, trial=True, support_team_id=support_team.id)
        except MaximumTrialDBException:
            url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_maximumtrialdb', '/')
            return werkzeug.utils.redirect(url)

        values = {
            'plan': trial_plan,
        }

        return request.render('saas_portal.try_trial', values)
