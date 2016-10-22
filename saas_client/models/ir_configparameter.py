# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.tools import mute_logger


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model_cr
    @mute_logger('odoo.addons.base.ir.ir_config_parameter')
    def init(self, force=False):
        super(IrConfigParameter, self).init(force=force)
        if force:
            oauth_oe = self.env.ref('saas_client.saas_oauth_provider')
            dbuuid = self.get_param('database.uuid')
            oauth_oe.write({'client_id': dbuuid})
