# -*- coding: utf-8 -*-
from odoo import api
from odoo import models
import psycopg2

import logging
_logger = logging.getLogger(__name__)


class SaasServerClient(models.Model):
    _inherit = 'saas_server.client'

    @api.multi
    def _rotate_backups(self, rotation_scheme):
        return

    @api.model
    def rotate_backups(self):

        config_parameter = self.env["ir.config_parameter"]
        unlimited = bool(int(config_parameter.get_param('saas_server_backup_rotate.backup_rotate_unlimited', False)))
        if unlimited:
            _logger.info('You have asked me not to rotate backups thus I am quitting')
            return

        backup_rotate_yearly = int(config_parameter.get_param('saas_server_backup_rotate.backup_rotate_yearly', default=2))
        backup_rotate_monthly = int(config_parameter.get_param('saas_server_backup_rotate.backup_rotate_monthly', default=12))
        backup_rotate_weekly = int(config_parameter.get_param('saas_server_backup_rotate.backup_rotate_weekly', default=4))
        backup_rotate_daily = int(config_parameter.get_param('saas_server_backup_rotate.backup_rotate_daily', default=7))
        backup_rotate_hourly = int(config_parameter.get_param('saas_server_backup_rotate.backup_rotate_hourly', default=24))

        rotation_scheme = {}

        if backup_rotate_hourly:
            rotation_scheme['hourly'] = backup_rotate_hourly
        if backup_rotate_daily:
            rotation_scheme['daily'] = backup_rotate_daily
        if backup_rotate_weekly:
            rotation_scheme['weekly'] = backup_rotate_weekly
        if backup_rotate_monthly:
            rotation_scheme['monthly'] = backup_rotate_monthly
        if backup_rotate_yearly:
            rotation_scheme['yearly'] = backup_rotate_yearly

        _logger.info("Parsed rotation scheme: %s", rotation_scheme)

        clients = self.search([('state', '!=', 'delete')])
        clients._rotate_backups(rotation_scheme)
