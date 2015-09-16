# -*- coding: utf-8 -*-
from openerp import models, fields, api, SUPERUSER_ID, exceptions


class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'

    termination_protection = fields.Boolean('Termination Protection', default=False,
                                            help='Protect from accidental deletion')
    
    @api.multi 
    def _check_termination_protection(self):
        for database in self:
            if database.termination_protection:
                raise exceptions.Warning('Termination Protection is enabled for client; '
                                   'If you wish to proceed please turn protection off')
    
    @api.multi
    def delete_database(self):
        self._check_termination_protection()
        return super(SaasPortalClient, self).delete_database()
    
    @api.multi
    def unlink(self):
        self._check_termination_protection()
        return super(SaasPortalClient, self).unlink()

