# -*- coding: utf-8 -*-
from openerp import api
from openerp import fields
from openerp import models


class SaasSubscriptionLog(models.Model):
    _name = 'saas_portal.subscription_log'
    _order = 'expiration_new desc'

    client_id = fields.Many2one('saas_portal.client', string='Client DB', readonly=True)
    expiration = fields.Datetime('Previous expiration', readonly=True)
    expiration_new = fields.Datetime('New expiration', readonly=True)
    reason = fields.Text(string='Reason', help='The reason of expiration change', readonly=True)
