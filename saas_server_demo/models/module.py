# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.addons.base.module.module import module as A


class ModuleDemo(models.Model):
    _inherit = "ir.module.module"

    demo_addons = fields.Char(string='Demo addons', help='Comma-separated string of modules technical names')
    demo_addons_hidden = fields.Char(string='Demo addons hidden', help='Comma-separated string of modules technical names')
    demo_url = fields.Char(string='Demo url')
    demo_title = fields.Char(string='Title of a demo set. Also title for demo product on the portal')
    price = fields.Float(string='Price', default=0)
    currency = fields.Char("Currency", help="The currency the field is expressed in.")

    @staticmethod
    def get_values_from_terp(terp):
        res = A.get_values_from_terp(terp)
        res.update({
                    'demo_title': terp.get('demo_title', False),
                    'demo_addons': ','.join(terp.get('demo_addons', [])),
                    'demo_addons_hidden': ','.join(terp.get('demo_addons_hidden', [])),
                    'demo_url': terp.get('demo_url', False),
                    'price': terp.get('price', False),
                    'currency': terp.get('currency', False),
                    })
        return res
