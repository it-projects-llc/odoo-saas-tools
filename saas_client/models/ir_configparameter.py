# -*- coding: utf-8 -*-
from openerp import models, api, tools, SUPERUSER_ID


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    def init(self, cr, force=False):
        super(IrConfigParameter, self).init(cr, force=force)
        if force:
            IMD = self.pool['ir.model.data']
            oauth_oe = IMD.xmlid_to_object(cr, SUPERUSER_ID,
                                           'saas_server.saas_oauth_provider')
            dbuuid = self.get_param(cr, SUPERUSER_ID, 'database.uuid')
            oauth_oe.write({'client_id': dbuuid})

    @tools.ormcache(skiparg=0)
    def get_saas_client_parameters(self, db):
        param_model = self.pool['ir.config_parameter']
        cr = self.pool.cursor()
        suspended = "0"
        try:
            suspended = param_model.get_param(
                cr, SUPERUSER_ID, 'saas_client.suspended', '0')
        finally:
            cr.close()
        return suspended

    @api.multi
    def write(self, vals, context=None):
        res = super(IrConfigParameter, self).write(vals)
        if self.key in ['saas_client.suspended']:
            self.get_saas_client_parameters.clear_cache(self)
        return res
