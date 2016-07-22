# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.addons.base.module.module import module as A


class ModuleDemo(models.Model):
    _inherit = "ir.module.module"

    demo_demonstrative = fields.Boolean('Is this module demonstrative', default=False)
    demo_addons = fields.Char(string='Demo addons', help='Comma-separated string of modules technical names')
    demo_addons_hidden = fields.Char(string='Demo addons hidden', help='Comma-separated string of modules technical names')
    demo_url = fields.Char(string='Demo url')

    @staticmethod
    def get_values_from_terp(terp):
        res = A.get_values_from_terp(terp)
        res.update({'demo_demonstrative': terp.get('demo_demonstrative', False),
                    'demo_addons': ','.join(terp.get('demo_addons', [])),
                    'demo_addons_hidden': ','.join(terp.get('demo_addons_hidden', [])),
                    'demo_url': terp.get('demo_url', False),
                    })
        return res
