# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from openerp import models, fields, api


class SaasSubscriptionWizard(models.TransientModel):
    _name = 'saas_portal.subscription_wizard'

    client_id = fields.Many2one('saas_portal.client', string='Client DB', readonly=True)
    expiration = fields.Datetime('Current expiration', readonly=True)
    expiration_new = fields.Datetime('New expiration', help='set new expiration here')
    reason = fields.Text(string='Reason of new expiration', help='The reason of expiration change')

    @api.multi
    def change_expiration(self):
        if self.expiration_new:
            self.client_id.upgrade(payload={'params':
                                   [{'key': 'saas_client.expiration_datetime',
                                     'value': self.expiration_new, 'hidden': True}]}
                            )
            # the code below will be executed only if client_id.upgrade doesn't
            # raise an exception i.e. the request has sacceeded
            expiration = fields.Datetime.from_string(self.expiration)
            expiration_new = fields.Datetime.from_string(self.expiration_new)
            self.client_id.period_manual += (expiration_new - expiration).days
            print '\n\n\n', 'in change_expiration ', 'period_manual ', self.client_id.period_manual, '\n\n\n'
            log_obj = self.env['saas_portal.subscription_log']
            log_obj.create({
                            'client_id': self.client_id.id,
                            'expiration': self.expiration,
                            'expiration_new': self.expiration_new,
                            'reason': self.reason,
                          })



