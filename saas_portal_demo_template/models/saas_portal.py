# -*- coding: utf-8 -*-
from openerp import models, fields, api

class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'

    @api.model
    def try_spurn_demo_instance(self):
        company = self.env.user.company_id
        if not company.demo_client_name or not company.demo_plan_id:
            return
        
        existing = self.search([('name', '=', company.demo_client_name)])
        if existing:
            existing.delete_database_server()
        
        res = company.demo_plan_id.create_new_database(
            dbname=company.demo_client_name)
        client = self.browse(res.get('id'))
        client.server_id.action_sync_server()
        