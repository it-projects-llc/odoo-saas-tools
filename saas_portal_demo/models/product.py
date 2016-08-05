# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ProductVariant(models.Model):
    _inherit = 'product.product'

    variant_plan_id = fields.Many2one('saas_portal.plan', string='Plan for Variant', ondelete='cascade')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    module_name = fields.Char('Module name', help='Demo module technical name')
