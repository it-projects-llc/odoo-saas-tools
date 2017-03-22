# -*- coding: utf-8 -*-
from openerp import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    saas_template_id = fields.Many2one('saas_portal.database', 'Template', ondelete='restrict')
