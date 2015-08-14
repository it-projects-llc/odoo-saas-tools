# -*- coding: utf-8 -*-
from openerp import models, fields, api


class SaasPortalPlan(models.Model):
    _name = 'saas_portal.plan'
    _inherit = 'saas_portal.plan'
    
    page_url = fields.Char('Page URL', placeholder='some-name')
    odoo_version = fields.Char('Odoo Version', placeholder='8.0')
    app_store_module_ids = fields.Many2many('saas_portal.module',
                                            'saas_portal_plan_module',
                                            'plan_id', 'module_id',
                                            'Modules')


class SaaSPortalModule(models.Model):
    _name = 'saas_portal.module'
    
    name = fields.Char('Name', placeholder='Reminders and Agenda (technical core)')
    technical_name = fields.Char('Technical Name', placeholder='reminder_base')
    summary = fields.Text('Summary')
    author = fields.Char('Author', placeholder='Ivan Yelizariev')
    module_id = fields.Many2one('ir.module.module', required=False)
    
    @api.onchange('module_id')
    def onchange_module_id(self):
        if self.module_id:
            self.name = self.module_id.shortdesc
            self.technical_name = self.module_id.name
            self.summary = self.module_id.summary
            self.author = self.module_id.author
        else:
            self.name, self.technical_name, self.summary, self.author  = [False] * 4
            
    _sql_constraints = [
        ('technical_name_uniq', 'unique(technical_name)', 'The module already exists!'),
    ]
