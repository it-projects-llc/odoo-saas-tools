# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductTemplateSaaS(models.Model):
    _inherit = 'product.template'

    plan_id = fields.Many2one('saas_portal.plan', string='Plan')  # obsolete

    plan_ids = fields.One2many('saas_portal.plan', 'product_tmpl_id',
                                string='SaaS Plans',
                                help='Create db per each selected plan - use the DB Names prefix setting in each selected plans')
    saas_default = fields.Boolean('Is default', help='Use as default SaaS product on signup form')
    on_create_email_template = fields.Many2one('mail.template', string='credentials mail')


class ProductAttributeSaaS(models.Model):
    _inherit = "product.attribute"

    saas_code = fields.Selection('_get_saas_codes')

    def _get_saas_codes(self):
        return [('SUBSCRIPTION_PERIOD', 'SUBSCRIPTION_PERIOD'),
                ('MAX_USERS', 'MAX_USERS'),
                ('INSTALL_MODULES', 'INSTALL_MODULES'),
                ('STORAGE_LIMIT', 'STORAGE_LIMIT')]


class ProductAttributeValueSaaS(models.Model):
    _inherit = "product.attribute.value"

    saas_code_value = fields.Char('SaaS code value')
