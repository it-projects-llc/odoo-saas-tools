# -*- coding: utf-8 -*-
from openerp import models, fields, api, SUPERUSER_ID, exceptions


class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'

    termination_protection = fields.Boolean('Termination Protection',
                                            help='Protect from accidental deletion')

    @api.multi
    def unlink(self):
        for client in self:
            if client.termination_protection:
                raise exceptions.Warning('Termination Protection is enabled for client; '
                                   'If you wish to proceed please turn protection off')
        return super(SaasPortalClient, self).unlink()
