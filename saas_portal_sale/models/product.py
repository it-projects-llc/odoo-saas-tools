# -*- coding: utf-8 -*-
from openerp import models, fields


class ProductTemplateSaaS(models.Model):
    _inherit = 'product.template'

    plan_id = fields.Many2one('saas_portal.plan', string='Plan')


class ProductAttributeSaaS(models.Model):
    _inherit = "product.attribute"

    saas_code = fields.Char('SaaS code')


class ProductAttributeValueSaaS(models.Model):
    _inherit = "product.attribute.value"

    saas_code_value = fields.Char('SaaS code value')
