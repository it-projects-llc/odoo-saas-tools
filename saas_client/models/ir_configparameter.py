# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp import models


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
