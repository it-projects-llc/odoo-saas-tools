from odoo import models, fields, api


class SaasServerWizard(models.TransientModel):
    _inherit = 'res.config.settings'

    backup_rotate_unlimited = fields.Boolean(
        'Unlimited Backup',
        description='Allow for unlimited backup'
    )
    backup_rotate_yearly = fields.Integer(
        'Yearly Count',
        description='Set the number of yearly backups to preserve during rotation'
    )
    backup_rotate_monthly = fields.Integer(
        'Monthly Count',
        description='Set the number of monthly backups to preserve during rotation'
    )
    backup_rotate_weekly = fields.Integer(
        'Weekly Count',
        description='Set the number of weekly backups to preserve during rotation'
    )
    backup_rotate_daily = fields.Integer(
        'Daily Count',
        description='Set the number of daily backups to preserve during rotation'
    )
    backup_rotate_hourly = fields.Integer(
        'Hourly Count',
        description='Set the number of hourly backups to preserve during rotation'
    )

    @api.multi
    def set_values(self):
        super(SaasServerWizard, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("saas_server.backup_rotate_unlimited", str(int(self.backup_rotate_unlimited)))
        ICPSudo.set_param("saas_server.backup_rotate_yearly", self.backup_rotate_yearly)
        ICPSudo.set_param("saas_server.backup_rotate_monthly", self.backup_rotate_monthly)
        ICPSudo.set_param("saas_server.backup_rotate_weekly", self.backup_rotate_weekly)
        ICPSudo.set_param("saas_server.backup_rotate_daily", self.backup_rotate_daily)
        ICPSudo.set_param("saas_server.backup_rotate_hourly", self.backup_rotate_hourly)

    @api.model
    def get_values(self):
        res = super(SaasServerWizard, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            backup_rotate_unlimited=bool(int(ICPSudo.get_param('saas_server.backup_rotate_unlimited', False))),
            backup_rotate_yearly=ICPSudo.get_param('saas_server.backup_rotate_yearly', default=2),
            backup_rotate_monthly=ICPSudo.get_param('saas_server.backup_rotate_monthly', default=12),
            backup_rotate_weekly=ICPSudo.get_param('saas_server.backup_rotate_weekly', default=4),
            backup_rotate_daily=ICPSudo.get_param('saas_server.backup_rotate_daily', default=7),
            backup_rotate_hourly=ICPSudo.get_param('saas_server.backup_rotate_hourly', default=24),
        )
        return res
