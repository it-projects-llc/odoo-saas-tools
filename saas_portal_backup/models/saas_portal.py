# -*- coding: utf-8 -*-
from openerp import models, fields, api


class SaasPortalDatabase(models.Model):
    _inherit = 'saas_portal.database'

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
        return super(SaasPortalDatabase, self).delete_database()


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
        return super(SaasPortalDatabase, self).delete_database()
