# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaasServerWizard(models.TransientModel):
    _inherit = 'saas_server.config.settings'

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

    @api.model
    def get_default_backup_rotate_strategy(self, fields):
        config_parameter = self.env["ir.config_parameter"]
        return {
            'backup_rotate_yearly': int(config_parameter.get_param('saas_server_backup_rotate.backup_rotate_yearly', default=2)),
            'backup_rotate_monthly': int(config_parameter.get_param('saas_server_backup_rotate.backup_rotate_monthly', default=12)),
            'backup_rotate_weekly': int(config_parameter.get_param('saas_server_backup_rotate.backup_rotate_weekly', default=4)),
            'backup_rotate_daily': int(config_parameter.get_param('saas_server_backup_rotate.backup_rotate_daily', default=7)),
            'backup_rotate_hourly': int(config_parameter.get_param('saas_server_backup_rotate.backup_rotate_hourly', default=24)),
            'backup_rotate_unlimited': bool(int(config_parameter.get_param('saas_server_backup_rotate.backup_rotate_unlimited', False))),
        }

    @api.one
    def set_backup_rotate_strategy(self):
        config_parameter = self.env["ir.config_parameter"]
        config_parameter.set_param('saas_server_backup_rotate.backup_rotate_yearly', self.backup_rotate_yearly)
        config_parameter.set_param('saas_server_backup_rotate.backup_rotate_monthly', self.backup_rotate_monthly)
        config_parameter.set_param('saas_server_backup_rotate.backup_rotate_weekly', self.backup_rotate_weekly)
        config_parameter.set_param('saas_server_backup_rotate.backup_rotate_daily', self.backup_rotate_daily)
        config_parameter.set_param('saas_server_backup_rotate.backup_rotate_hourly', self.backup_rotate_hourly)
        config_parameter.set_param('saas_server_backup_rotate.backup_rotate_unlimited', str(int(self.backup_rotate_unlimited)))
