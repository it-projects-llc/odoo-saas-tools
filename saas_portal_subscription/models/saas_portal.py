from datetime import timedelta
from odoo import api, fields, models


class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'

    expiration_datetime = fields.Datetime(
        'Expiration', compute='_compute_expiration', store=True)
    expiration_datetime_sent = fields.Datetime(
        'Expiration sent', readonly=True)
    subscription_log_ids = fields.One2many(
        'saas_portal.subscription_log', 'client_id', 'Subscription log',
        readonly=True)

    @api.multi
    @api.depends('create_date', 'subscription_log_ids', 'trial')
    def _compute_expiration(self):
        for record in self:
            expiration = (
                fields.Datetime.from_string(record.create_date) +
                record.get_subscription_log_timedelta() +
                timedelta(record.plan_id.grace_period)
            )
            if record.trial:
                expiration += timedelta(hours=record.plan_id.expiration)
            record.expiration_datetime = fields.Datetime.to_string(expiration)

    @api.multi
    def change_subscription(self, expiration, reason):
        log_obj = self.env['saas_portal.subscription_log']
        for record in self:
            if record.expiration_datetime != expiration:
                # after expiration_datetime is computed on subscription_log_ids
                # change base.automation triggers send_expiration_info with
                # record.upgrade
                log_obj.create({
                    'client_id': record.id,
                    'expiration': record.expiration_datetime,
                    'expiration_new': expiration,
                    'reason': reason,
                })

    @api.multi
    def get_subscription_log_timedelta(self):
        self.ensure_one()
        td = timedelta()
        for log in self.subscription_log_ids:
            td += (fields.Datetime.from_string(log.expiration_new) -
                   fields.Datetime.from_string(log.expiration))
        return td

    @api.multi
    def send_expiration_info(self):
        for record in self:
            if (record.state not in ('draft', 'deleted') and
                    record.expiration_datetime and
                    record.expiration_datetime_sent !=
                    record.expiration_datetime):
                record.expiration_datetime_sent = record.expiration_datetime

                record.upgrade(record.get_upgrade_database_payload())
                record.send_expiration_info_to_partner()

                # expiration date has been changed, flush expiration
                # notification flag
                record.notification_sent = False
