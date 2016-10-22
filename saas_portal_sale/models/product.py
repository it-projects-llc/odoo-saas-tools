# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductTemplateSaaS(models.Model):
    _inherit = 'product.template'

    plan_id = fields.Many2one('saas_portal.plan', string='Plan')


class ProductAttributeSaaS(models.Model):
    _inherit = "product.attribute"

    saas_code = fields.Selection('_get_saas_codes')

    def _get_saas_codes(self):
        return [('SUBSCRIPTION_PERIOD', 'SUBSCRIPTION_PERIOD'),
                ('MAX_USERS', 'MAX_USERS'),
                ('INSTALL_MODULES', 'INSTALL_MODULES'),
                ('STORAGE_LIMIT', 'STORAGE_LIMIT')]
    # saas_code = fields.Char('SaaS code', help='''Possible codes:
    # * SUBSCRIPTION_PERIOD
    # * MAX_USERS
    # * INSTALL_MODULES
    # * STORAGE_LIMIT
    # ''')


class ProductAttributeValueSaaS(models.Model):
    _inherit = "product.attribute.value"

    saas_code_value = fields.Char('SaaS code value')
