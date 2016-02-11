# -*- coding: utf-8 -*-
from openerp import models, fields, api


class SaasTagClient(models.TransientModel):
    _name = 'saas_portal.modify_backup'
    
    @api.model
    def _default_backup_strategy(self):
        client = self.env['saas_portal.client'].browse(
            self.env.context['active_id'])
        return client.backup
    
    backup = fields.Boolean(
        'Backup on Modify',
        help="Backs up first before deleting or upgrading",
        default=_default_backup_strategy
    )

    @api.multi
    def apply(self):
        self.ensure_one()
        client = self.env['saas_portal.client'].browse(
            self.env.context['active_id'])
        client.write({'backup': self.backup})
        return True
