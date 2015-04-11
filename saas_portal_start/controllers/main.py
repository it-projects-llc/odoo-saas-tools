# -*- coding: utf-8 -*-
import openerp
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.auth_oauth.controllers import main as oauth
import werkzeug
import simplejson
import uuid
import random

class SaasPortal(http.Controller):

    @http.route(['/page/website.start', '/page/start'], type='http', auth="public", website=True)
    def start(self, **post):
        base_saas_domain = self.get_config_parameter('base_saas_domain')
        values = {'base_saas_domain': base_saas_domain}
        return request.website.render("website.start", values)

    def get_config_parameter(self, param):
        # FIXME: undublicate this function. Use one from saas_portal
        config = request.registry['ir.config_parameter']
        full_param = 'saas_portal.%s' % param
        return config.get_param(request.cr, SUPERUSER_ID, full_param)
