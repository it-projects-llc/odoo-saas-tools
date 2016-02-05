# -*- coding: utf-8 -*-
from openerp.addons.web import http
from openerp.addons.web.http import request
import werkzeug
from openerp.addons.saas_portal.controllers.main import SaasPortal


class SaasPortalSale(SaasPortal):

    @http.route(['/saas_portal/add_new_client'], type='http', auth='user', website=True)
    def add_new_client(self, **post):
        plan = self.get_plan(int(post.get('plan_id', 0) or 0))

        if not plan.free_subdomains:
            dbname = self.get_full_dbname(post.get('dbname'))
            user_id = request.session.uid
            partner_id = None
            if user_id:
                user = request.env['res.users'].browse(user_id)
                partner_id = user.partner_id.id

            lines = request.env['saas_portal.find_payments_wizard'].find_partner_payments(partner_id=partner_id, plan_id=plan.id)
            if len(lines) == 0:
                url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_nonfree_subdomains', '/')
                return werkzeug.utils.redirect(url)

        return super(SaasPortalSale, self).add_new_client(**post)

