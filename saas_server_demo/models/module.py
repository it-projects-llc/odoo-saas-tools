# -*- coding: utf-8 -*-
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
    demo_image_url = fields.Char('Demo image URL')
    demo_image = fields.Binary(compute="_compute_demo_image")

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
                    })
        return res

    @api.multi
    def _compute_demo_image(self):
        for record in self:
            path = get_module_resource(record.name, 'static', 'description', 'demo_image.png')
            if path:
                image_file = tools.file_open(path, 'rb')
                try:
                    record.demo_image = image_file.read().encode('base64')
                finally:
                    image_file.close()
