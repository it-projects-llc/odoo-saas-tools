# -*- coding: utf-8 -*-
import werkzeug
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.saas_portal.controllers.main import SaasPortal
from openerp.addons.website_sale.controllers.main import website_sale, QueryURL


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
        if version:
            attr_id = request.env.ref('saas_portal_demo.odoo_version_product_attribute').id
            var_id = request.env['product.attribute.value'].search([('attribute_id', '=', attr_id),('name', '=', version)]).id
            url = request.httprequest.url.split('?', 1)[0] + '?attrib=%s-%s' % (attr_id, var_id)
            return werkzeug.utils.redirect(url)

        if product.saas_demo:
            odoo_version_attrib = request.env['product.attribute'].search([('name', '=', 'Odoo Version')], limit=1)
            odoo_version_value_ids = request.env['product.attribute.value'].search([('attribute_id', '=', odoo_version_attrib.id)])
            demo_variants = product.product_variant_ids.mapped('attribute_value_ids').filtered(lambda r: odoo_version_attrib.id == r.attribute_id.id).ids

            # part copied from website_sale /shop/product controller begin
            cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
            category_obj = pool['product.public.category']
            template_obj = pool['product.template']

            context.update(active_id=product.id)

            if category:
                category = category_obj.browse(cr, uid, int(category), context=context)
                category = category if category.exists() else False

            attrib_list = request.httprequest.args.getlist('attrib')
            attrib_values = [map(int,v.split("-")) for v in attrib_list if v]
            attrib_set = set([v[1] for v in attrib_values])

            keep = QueryURL('/shop', category=category and category.id, search=search, attrib=attrib_list)

            category_ids = category_obj.search(cr, uid, [], context=context)
            category_list = category_obj.name_get(cr, uid, category_ids, context=context)
            category_list = sorted(category_list, key=lambda category: category[1])

            pricelist = self.get_pricelist()

            from_currency = pool.get('product.price.type')._get_field_currency(cr, uid, 'list_price', context)
            to_currency = pricelist.currency_id
            compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price, context=context)

            if not context.get('pricelist'):
                context['pricelist'] = int(self.get_pricelist())
                product = template_obj.browse(cr, uid, int(product), context=context)
            # end part copied

            values = {
                'demo_variants': demo_variants,
                'odoo_version_attrib': odoo_version_attrib,
                'search': search,
                'category': category,
                'pricelist': pricelist,
                'attrib_values': attrib_values,
                'compute_currency': compute_currency,
                'attrib_set': attrib_set,
                'keep': keep,
                'category_list': category_list,
                'main_object': product,
                'product': product,
                'get_attribute_value_ids': self.get_attribute_value_ids

            }
            return request.website.render("website_sale.product", values)

        return super(website_sale_custom, self).product(product=product, category=category, search=search, **kwargs)
