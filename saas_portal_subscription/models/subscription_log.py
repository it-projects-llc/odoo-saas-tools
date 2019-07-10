from odoo import fields, models


class SaasSubscriptionLog(models.Model):
    _name = 'saas_portal.subscription_log'
    _order = 'id desc'

    client_id = fields.Many2one('saas_portal.client', 'Client')
    expiration = fields.Datetime('Previous expiration')
    expiration_new = fields.Datetime('New expiration')
    reason = fields.Text('Reason')
