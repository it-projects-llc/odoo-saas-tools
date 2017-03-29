# -*- coding: utf-8 -*-
from openerp import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    plan_ids = fields.Many2many('saas_portal.plan',
                                string='SaaS Plans',
                                help='Create db per each selected plan - use the DB Names prefix setting in each selected plans')
    saas_default = fields.Boolean('Use as default SaaS product')
