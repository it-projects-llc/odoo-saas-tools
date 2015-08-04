# -*- coding: utf-8 -*-
from openerp import models, fields


class SaasPortalPlan(models.Model):
    _name = 'saas_portal.plan'
    _inherit = 'saas_portal.plan'
    
    page_url = fields.Char('Page URL', placeholder='module-xxx')
    odoo_version = fields.Char('Odoo Version', placeholder='8.0')
