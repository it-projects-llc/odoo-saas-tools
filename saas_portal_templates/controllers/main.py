# -*- coding: utf-8 -*-
import openerp
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.auth_oauth.controllers import main as oauth
from openerp.addons.web.controllers.main import login_redirect
from openerp.addons.saas_portal.controllers.main import SaasPortal as saas_portal_controller

import werkzeug
import simplejson
import uuid
import random


class SaasPortalTemplates(saas_portal_controller):

    @http.route(['/saas_portal_templates/select-template'], type='http', auth='public', website=True)
    def select_template(self, **post):
        cr, uid = request.cr, SUPERUSER_ID
        domain = [('state', 'in', ['confirmed'])]
        templates = request.registry['saas_portal.plan'].search_read(cr, uid, domain, fields=['id', 'name'])
        values = {'templates': templates}
        return request.website.render("saas_portal_templates.select_template", values)

    @http.route(['/saas_portal_templates/new_database'], type='http', auth='public', website=True)
    def new_database(self, **post):
        if not request.session.uid:
            return login_redirect()
        plan_id = int(post.get('plan_id'))

        return self.create_demo_database(plan_id)
