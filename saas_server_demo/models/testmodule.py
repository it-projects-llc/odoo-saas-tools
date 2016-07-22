from openerp.addons.base.module.module import module as A
from openerp import models, fields, api


class moduletest(models.Model):
    _inherit = "ir.module.module"

    @staticmethod
    def get_values_from_terp(terp):
        res = A.get_values_from_terp(terp)
        res.update({'demo_demonstrative': terp.get('demo_demonstrative', '')})
        print '\n\n\n', 'in get_values_from_terp ', 'res ', res, '\n\n\n'
        return res
