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
        plan = self.get_default_plan()
        url = plan._create_new_database(dbname)[0]
        return werkzeug.utils.redirect(url)

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
