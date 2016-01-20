# -*- coding: utf-8 -*-
from openerp import models, fields


class ProductTemplateSaaS(models.Model):
    _inherit = 'product.template'

    plan_id = fields.Many2one('saas_portal.plan', string='Plan')
    period = fields.Integer(string='Subscription period')
    subscription_per_user = fields.Boolean(default=False, help='product quantity serves as a max users allowed to the client')
