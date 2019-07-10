from odoo import api, fields, models


class SaasSubscriptionWizard(models.TransientModel):
    _name = 'saas_portal.subscription_wizard'

    client_id = fields.Many2one('saas_portal.client', 'Client', readonly=True)
    expiration = fields.Datetime('Current expiration', readonly=True)
    expiration_new = fields.Datetime('New expiration', required=True)
    reason = fields.Text(string='Reason', required=True)

    @api.model
    def default_get(self, fields):
        result = super(SaasSubscriptionWizard, self).default_get(fields)
        client = self.env['saas_portal.client'].browse(
            self.env.context.get('active_id'))
        result['client_id'] = client.id
        result['expiration'] = client.expiration_datetime
        result['expiration_new'] = client.expiration_datetime
        return result

    @api.multi
    def apply_changes(self):
        if self.expiration_new != self.expiration:
            self.client_id.change_subscription(
                self.expiration_new, self.reason)
