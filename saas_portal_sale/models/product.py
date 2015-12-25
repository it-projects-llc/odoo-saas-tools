# -*- coding: utf-8 -*-
from openerp import models, fields


class ProductTemplateSaaS(models.Model):
    _inherit = 'product.template'

    plan_id = fields.Many2one('saas_portal.plan', string='Plan')
    period = fields.Integer(string='Subscription period')
