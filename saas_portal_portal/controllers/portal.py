from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        SaasPortalClient = request.env['saas_portal.client']

        instance_count = SaasPortalClient.search_count([
            ('partner_id', '=', partner.id),
        ])

        values.update({
            'instance_count': instance_count,
        })
        return values

    @http.route(['/my/instances', '/my/instances/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_instances(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaasPortalClient = request.env['saas_portal.client']
        instances = SaasPortalClient.sudo().search([('partner_id.id', '=', partner.id)])

        values.update({
            'instances': instances,
        })
        return request.render("saas_portal_portal.portal_my_instances", values)

    @http.route("/my/domain/<int:instance_id>", type='http', auth="user", website=True)
    def change_domain(self, instance_id, **post):
        instance = request.env['saas_portal.client'].sudo().browse(instance_id)
        ICPsudo = request.env['ir.config_parameter'].sudo()
        base_saas_domain = ICPsudo.get_param('base_saas_domain')
        values = {
            'domain_name': instance.name,
            'saas_portal_client': instance,
            'base_saas_domain': base_saas_domain,
        }
        return request.render("saas_portal_portal.change_domain", values)
