# -*- coding: utf-8 -*-
import werkzeug
from odoo import http
from odoo.http import request
from odoo.addons.saas_portal.controllers.main import SaasPortal
from odoo.addons.website_sale.controllers.main import WebsiteSale as website_sale


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


class website_sale_custom(website_sale):

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        version = kwargs.get('version')
        attr_id = request.env.ref('saas_portal_demo.odoo_version_product_attribute').id
        if version:
            var_id = request.env['product.attribute.value'].search([('attribute_id', '=', attr_id),('name', '=', version)]).id
            url = request.httprequest.url.split('?', 1)[0] + '?attrib=%s-%s' % (attr_id, var_id)
            return werkzeug.utils.redirect(url)
        if product.saas_demo and not '?' in request.httprequest.url:
            attr_vals = product.product_variant_ids.mapped('attribute_value_ids').filtered(lambda r: r.attribute_id.id == attr_id)
            vals_dict = {val: int(val.split('.', 1)[0]) for val in attr_vals.mapped('name')}
            max_version = max(vals_dict, key=vals_dict.get)
            url = request.httprequest.url + '?version=' + max_version
            return werkzeug.utils.redirect(url)

        return super(website_sale_custom, self).product(product=product, category=category, search=search, **kwargs)
