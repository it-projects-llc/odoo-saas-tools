# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api
from openerp.addons.saas_utils import connector, database
from openerp import http
from contextlib import closing

class SaasPricingPrice(models.Model):
    _name = 'saas_pricing.price'
    
    name = fields.Char('Price name')
    price = fields.Float('Price', digits=(16,2))
    
class SaasPricingPlan(models.Model):
    _inherit = 'saas_server.plan'
    
    pricing_ids = fields.Many2many('saas_pricing.price', 'saas_pricing_plan')
    
    
