# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo import tools, _
from odoo.exceptions import Warning as UserError

import logging
_logger = logging.getLogger(__name__)
try:
    import pysftp
except ImportError:
    _logger.debug('saas_server_backup_ftp requires the python library pysftp which is not found on your installation')


class SaasPortalConfigWizard(models.TransientModel):
    _inherit = 'saas_server.config.settings'

    sftp_server = fields.Char(string='SFTP Server Address', help='IP address of your remote server. For example 192.168.0.1')
    sftp_username = fields.Char(string='Username on SFTP Server', help="The username where the SFTP connection should be made with. This is the user on the external server.")
    sftp_password = fields.Char(string='Password User SFTP Server', help="The password from the user where the SFTP connection should be made with. This is the password from the user on the external server.")
    sftp_path = fields.Char(string='Path external server', help="The location to the folder where the dumps should be written to. For example /odoo/backups/.\nFiles will then be written to /odoo/backups/ on your remote server.")
    sftp_rsa_key_path = fields.Char(
        string='Path rsa key',
        help="The location to the folder where the rsa key is saved. "
             "For example /opt/odoo/.ssh/id_rsa.")

    # sftp_rsa_key_path
    @api.model
    def get_default_sftp_rsa_key_path(self, fields):
        sftp_rsa_key_path = self.env["ir.config_parameter"].get_param(
            "saas_server.sftp_rsa_key_path")
        return {'sftp_rsa_key_path': sftp_rsa_key_path or False}

    @api.multi
    def set_sftp_rsa_key_path(self):
        config_parameters = self.env["ir.config_parameter"]
        for record in self:
            config_parameters.set_param("saas_server.sftp_rsa_key_path",
                                        record.sftp_rsa_key_path or '')
    # sftp_server
    @api.model
    def get_default_sftp_server(self, fields):
        sftp_server = self.env["ir.config_parameter"].get_param("saas_server.sftp_server", default=None)
        return {'sftp_server': sftp_server or False}

    @api.multi
    def set_sftp_server(self):
        config_parameters = self.env["ir.config_parameter"]
        for record in self:
            config_parameters.set_param("saas_server.sftp_server", record.sftp_server or '')

    # sftp_username
    @api.model
    def get_default_sftp_username(self, fields):
        sftp_username = self.env["ir.config_parameter"].get_param("saas_server.sftp_username", default=None)
        return {'sftp_username': sftp_username or False}

    @api.multi
    def set_sftp_username(self):
        config_parameters = self.env["ir.config_parameter"]
        for record in self:
            config_parameters.set_param("saas_server.sftp_username", record.sftp_username or '')

    # sftp_password
    @api.model
    def get_default_sftp_password(self, fields):
        sftp_password = self.env["ir.config_parameter"].get_param("saas_server.sftp_password", default=None)
        return {'sftp_password': sftp_password or False}

    @api.multi
    def set_sftp_password(self):
        config_parameters = self.env["ir.config_parameter"]
        for record in self:
            config_parameters.set_param("saas_server.sftp_password", record.sftp_password or '')

    # sftp_path
    @api.model
    def get_default_sftp_path(self, fields):
        sftp_path = self.env["ir.config_parameter"].get_param("saas_server.sftp_path", default=None)
        return {'sftp_path': sftp_path or False}

    @api.multi
    def set_sftp_path(self):
        config_parameters = self.env["ir.config_parameter"]
        for record in self:
            config_parameters.set_param("saas_server.sftp_path", record.sftp_path or '')

    def test_sftp_connection(self):
        server = self.env["ir.config_parameter"].get_param("saas_server.sftp_server", default=None)
        username = self.env["ir.config_parameter"].get_param("saas_server.sftp_username", default=None)
        password = self.env["ir.config_parameter"].get_param("saas_server.sftp_password", default=None)
        path = self.env["ir.config_parameter"].get_param("saas_server.sftp_path", default=None)
        sftp_rsa_key_path = self.env["ir.config_parameter"].get_param('saas_server.sftp_rsa_key_path')

        messageTitle = ""
        messageContent = ""

        try:
            # Connect with external server over SFTP, so we know sure that everything works.
            if sftp_rsa_key_path:
                srv = pysftp.Connection(host=server, username=username,
                                        private_key=sftp_rsa_key_path,
                                        private_key_pass=password)
            else:
                srv = pysftp.Connection(host=server, username=username, password=password)
            srv.close()
            # We have a success.
            messageTitle = "Connection Test Succeeded!"
            messageContent = "Everything seems properly set up for FTP back-ups!"
        except Exception as e:
            messageTitle = "Connection Test Failed!\n"
            messageContent += "Here is what we got instead:\n"
        if "Failed" in messageTitle:
            msg = _('{}{}{}'.format(messageTitle, messageContent, e))
            raise UserError(msg)
        else:
            _logger.info(_(messageTitle), _(messageContent))
