# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'

    backup = fields.Boolean('Backup on Modify', help="Backs up first before deleting \
                             or upgrading", default=True)

    @api.multi
    def action_backup(self):
        self.ensure_one()
        self._backup()

    @api.multi
    def delete_database(self):
        for database_obj in self:
            if database_obj.backup:
                database_obj._backup()
        return super(SaasPortalClient, self).delete_database()

    @api.multi
    def upgrade(self, payload=None):
        for database_obj in self:
            if database_obj.backup:
                # backup won't be done for upgrades through saas.config.do_upgrade_database
                # TODO: replace all saas.config.do_upgrade_database to self.upgrade
                database_obj._backup()
        return super(SaasPortalClient, self).upgrade(payload=payload)
