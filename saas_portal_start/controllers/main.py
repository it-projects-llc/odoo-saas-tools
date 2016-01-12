# -*- coding: utf-8 -*-
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.saas_portal.controllers.main import SaasPortal


class SaasPortalStart(SaasPortal):

    @http.route(['/page/website.start', '/page/start'], type='http', auth="public", website=True)
    def start(self, **post):
        base_saas_domain = self.get_config_parameter('base_saas_domain')
        values = {
            'base_saas_domain': base_saas_domain,
            'plan_id': post.get('plan_id')
        }
        return request.website.render("website.start", values)
