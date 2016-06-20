# -*- coding: utf-8 -*-
from openerp import models, fields, api


class SaasPortalPlan(models.Model):
    _name = 'saas_portal.plan'
    _inherit = 'saas_portal.plan'

    version_id = fields.Many2one('saas_portal.version', 'Version')

    addons_path_id = fields.Many2one('saas_portal.addons_path')

    module_version_ids = fields.Many2many('saas_portal.module',
                                          'saas_portal_plan_module',
                                          'plan_id', 'module_id',
                                          'Modules')


class SaaSPortalModule(models.Model):
    _name = 'saas_portal.module'
    _rec_name = 'technical_name'

    technical_name = fields.Char('Technical Name')
    module_version_ids = fields.One2many('saas_portal.module.version', 'module_id')

    _sql_constraints = [
        ('technical_name_uniq', 'unique(technical_name)', 'The module already exists!'),
    ]


class SaaSPortalModuleVersion(models.Model):
    _name = 'saas_portal.module.version'

    module_id = fields.Many2one('saas_portal.module', 'Module')
    name = fields.Char('Name')
    version_id = fields.Many2one('saas_portal.version', 'Version')
    summary = fields.Char('Summary')
    #author = fields.Char('Author')
    image_id = fields.Many2one('ir.attachment', 'Image')
    icon_id = fields.Many2one('ir.attachment', 'Icon')
    price = fields.Char('Char')
    currency = fields.Char('Currency')


class SaaSPortalVersion(models.Model):
    _name = 'saas_portal.version'

    _order = 'sequence'

    name = fields.Char('Name', required=True, help='Branded name of a version. Can be the same as technical name')
    technical_name = fields.Char('Technical Name', required=True, help='7.0, 8.0, 9.0 etc.')
    sequence = fields.Integer('Sequence')
    attribute_value = fields.Many2one('product.attribute.value', 'Attribute Value', help='Specify corresponded value for "Version" attribute')
