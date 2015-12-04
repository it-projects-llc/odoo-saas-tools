# -*- coding: utf-8 -*-
from ast import literal_eval
import openerp
from openerp import SUPERUSER_ID, exceptions
from openerp.tools.translate import _
from openerp.addons.web import http
from openerp.addons.web.http import request
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

    @http.route(['/saas_portal/add_new_client'], type='http', auth='public', website=True)
    def add_new_client(self, **post):
        dbname = self.get_full_dbname(post.get('dbname'))
        plan = self.get_plan(int(post.get('plan_id', 0)))
        res = plan.create_new_database(dbname)
        return werkzeug.utils.redirect(res.get('url'))

    def get_config_parameter(self, param):
        config = request.registry['ir.config_parameter']
        full_param = 'saas_portal.%s' % param
        return config.get_param(request.cr, SUPERUSER_ID, full_param)

    def get_full_dbname(self, dbname):
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
        if not uid:
            plan_id = int(kw.get('plan_id'))
            return http.local_redirect('/web/login?redirect=/trial'+'?plan_id='+str(plan_id))

        partner = request.env['res.users'].browse(uid).partner_id

        plan_id = int(kw.get('plan_id'))
        trial_plan = request.env['saas_portal.plan'].sudo().browse(plan_id)
        support_team = request.env.ref('saas_portal.main_support_team')
        res = trial_plan.create_new_database(partner_id=partner.id, user_id=uid, notify_user=True, trial=True, support_team_id=support_team.id)
        client = request.env['saas_portal.client'].sudo().browse(res.get('id'))
        client.server_id.action_sync_server()

        values = {
            'plan': trial_plan,
            'client': client,
        }

        return request.render('saas_portal.try_trial', values)
