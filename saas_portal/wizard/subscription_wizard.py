# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError


class SaasSubscriptionWizard(models.TransientModel):
    _name = 'saas_portal.subscription_wizard'

    client_id = fields.Many2one('saas_portal.client', string='Client DB', readonly=True)
    expiration = fields.Datetime('Current expiration', readonly=True)
    expiration_new = fields.Datetime('New expiration', help='set new expiration here')
    reason = fields.Text(string='Reason of new expiration', help='The reason of expiration change')

    @api.model
    def default_get(self, fields):
        result = super(SaasSubscriptionWizard, self).default_get(fields)
        client = self.env['saas_portal.client'].browse(self.env.context.get('active_id'))
        result['client_id'] = client.id
        result['expiration'] = client.expiration_datetime
        result['expiration_new'] = client.expiration_datetime
        return result

    @api.multi
    def apply_changes(self):
        if self.expiration_new:
            expiration = fields.Datetime.from_string(self.expiration)
            expiration_new = fields.Datetime.from_string(self.expiration_new)
            if expiration_new == expiration:
                return
            elif not self.reason:
                raise ValidationError('Please specify the reason of manual changes')
            else:
                self.client_id.change_subscription(expiration=self.expiration_new, reason=self.reason)
