# -*- coding: utf-8 -*-
import werkzeug
from odoo import http
from odoo.http import request
from odoo.addons.saas_portal.controllers.main import SaasPortal


def signup_redirect():
    url = '/web/signup?'
    redirect_url = '%s?%s' % (request.httprequest.base_url, werkzeug.urls.url_encode(request.params))
    return """<html><head><script>
        window.location = '%sredirect=' + encodeURIComponent("%s");
    </script></head></html>
    """ % (url, redirect_url)


class SaasPortalDemo(SaasPortal):

    @http.route(['/demo/<string:version>/<string:plan_url>/'], type='http', auth='public', website=True)
    def show_plan(self, version, plan_url, **post):
        domain = [('odoo_version', '=', version), ('page_url', '=', plan_url),
                  ('state', '=', 'confirmed')]
        plan = request.env['saas_portal.plan'].sudo().search(domain)
        if not plan:
            # TODO: maybe in this case we can redirect to saas_portal_templates.select_template
            return request.website.render("saas_portal_demo.unavailable_plan")
        values = {'plan': plan[0]}
        return request.website.render("saas_portal_demo.show_plan", values)
