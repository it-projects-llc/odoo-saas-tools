# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductTemplateSaaS(models.Model):
    _inherit = 'product.template'

    plan_ids = fields.One2many('saas_portal.plan', 'product_tmpl_id',
                                string='SaaS Plans',
                                help='Create db per each selected plan - use the DB Names prefix setting in each selected plans')
    saas_default = fields.Boolean('Is default', help='Use as default SaaS product on signup form')
    on_create_email_template = fields.Many2one('mail.template', string='credentials mail')
