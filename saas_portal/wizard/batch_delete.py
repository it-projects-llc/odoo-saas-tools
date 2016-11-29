# -*- coding: utf-8 -*-
from openerp import models, fields, api


class SaasBatchDeleteWizard(models.TransientModel):
    _name = 'saas_portal.batch_delete_wizard'

    def _default_client_ids(self):
        return self._context.get('active_ids')

    client_ids = fields.Many2many('saas_portal.client', 'saas_batch_delete_clients_rel', 'cid', 'did',
                                  readonly=True, default=_default_client_ids)

    @api.multi
    def delete_from_server(self):
        self.client_ids._delete_database_server()
