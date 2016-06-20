# -*- coding: utf-8 -*-
from openerp import models, fields, api

class AddonsPath(models.Model):
    _name = 'saas_portal.addons_path'

    odoo_version = fields.Char('Odoo Version', placeholder='8.0', default='8.0')
    path = fields.Char('Path', help='comma separated list of paths, where modules with__demo__.py can be found')
    publish = fields.Boolean('Publish on website after creating', default=True)
    sale_on_website = fields.Boolean('Show Add To Cart button', help='Switch it on, if you are going to use Plans to sale databases (e.g. via saas_portal_sale_online module)')

    plan_ids = fields.One2many('saas_portal.plan', 'addons_path_id')
