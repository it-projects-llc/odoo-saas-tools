# -*- coding: utf-8 -*-
import os
from os import walk

from odoo import models, fields, api, tools
from odoo.addons.base.module.module import Module as A
from odoo.modules import get_module_resource


class ModuleDemo(models.Model):
    _inherit = "ir.module.module"

    demo_addons = fields.Char(string='Demo addons', help='Comma-separated string of modules technical names')
    demo_addons_hidden = fields.Char(string='Demo addons hidden', help='Comma-separated string of modules technical names')
    demo_url = fields.Char(string='Demo url')
    demo_title = fields.Char(string='Title of a demo set. Also title for demo product on the portal')
    demo_summary = fields.Char(string='Demo set summary')
    price = fields.Float(string='Price', default=0)
    currency = fields.Char("Currency", help="The currency the field is expressed in.")
    demo_images = fields.Char(help="file names, the files should be placed in /static/description/demo of the module")
    installable = fields.Boolean()

    @staticmethod
    def get_values_from_terp(terp):
        res = A.get_values_from_terp(terp)
        res.update({
                    'demo_title': terp.get('demo_title', False),
                    'demo_summary': terp.get('demo_summary', False),
                    'demo_addons': ','.join(terp.get('demo_addons', [])),
                    'demo_addons_hidden': ','.join(terp.get('demo_addons_hidden', [])),
                    'demo_url': terp.get('demo_url', False),
                    'price': terp.get('price', False),
                    'currency': terp.get('currency', False),
                    'demo_images': ','.join(terp.get('demo_images', [])),
                    'installable': bool(terp.get('installable', False)),
                    })
        return res

    @api.multi
    def get_demo_images(self):
        self.ensure_one()
        demo_images = self.demo_images and self.demo_images.split(',')
        res = []
        mod_path = get_module_resource(self.name)
        for image_name in demo_images:
            full_name = os.path.join(mod_path, image_name)
            try:
                with tools.file_open(full_name, 'rb') as image_file:
                    res.append((image_name, image_file.read().encode('base64')))
            except:
                pass
        return res
