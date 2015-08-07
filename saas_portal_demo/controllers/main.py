# -*- coding: utf-8 -*-
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.web.controllers.main import login_redirect
from openerp.addons.saas_portal.controllers.main import SaasPortal


class SaasPortalDemo(SaasPortal):

    @http.route(['/demo/<string:version>/<string:plan_url>'], type='http', auth='public', website=True)
    def show_plan(self, version, plan_url, **post):
        domain = [('odoo_version', '=', version), ('page_url', '=', plan_url),
                  ('state', '=', 'confirmed')]
        plan = request.env['saas_portal.plan'].sudo().search(domain)
        if not plan:
            # TODO: maybe in this case we can redirect to saas_portal_templates.select_template
            return request.website.render("saas_portal_demo.unavailable_plan")
        values = {'plan': plan[0]}
        return request.website.render("saas_portal_demo.show_plan", values)

    @http.route('/demo/new_database', type='http', auth='public', website=True)
    def new_demo_database(self, **post):
        if not request.session.uid:
            return login_redirect()
        plan_id = int(post.get('plan_id'))

        return self.create_new_database(plan_id)
