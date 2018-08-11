from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal
import logging
_logger = logging.getLogger(__name__)


class WebsiteSaasDashboard(CustomerPortal):

    def _prepare_portal_layout_values(self):
        """ Add sales documents to main account page """
        values = super(WebsiteSaasDashboard, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        res_saas_portal_client = request.env['saas_portal.client']
        saas_portal_clients = res_saas_portal_client.sudo().search([
            ('partner_id', '=', partner.id),
        ])
        values.update({
            'saas_portal_clients': saas_portal_clients or False,
        })
        return values

    @http.route(['/my/domain'], type='http', auth='user', website=True)
    def change_domain(self, redirect=None, **post):
        partner = request.env['res.users'].browse(request.uid).partner_id
        partner = request.env.user.partner_id

        res_saas_portal_client = request.env['saas_portal.client']
        saas_portal_client = res_saas_portal_client.sudo().search([
            ('partner_id', '=', partner.id),
        ])
        config_obj = request.env['ir.config_parameter']
        base_saas_domain = config_obj.sudo().get_param('base_saas_domain')
        values = {
            'domain_name': saas_portal_client and saas_portal_client[0].name or False,
            'saas_portal_client': saas_portal_client and saas_portal_client[0] or False,
            'base_saas_domain': base_saas_domain,
        }
        return request.render("saas_portal_portal.change_domain", values)
