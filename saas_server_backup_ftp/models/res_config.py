from odoo import models, fields, api
from odoo import _, exceptions

import logging
_logger = logging.getLogger(__name__)
try:
    import pysftp
except ImportError:
    _logger.debug(
        '''saas_server_backup_ftp requires the python library
        pysftp which is not found on your installation''')


class SaasPortalConfigWizard(models.TransientModel):
    _inherit = 'res.config.settings'

    sftp_server = fields.Char(
        string='SFTP Server Address',
        help='IP address of your remote server. For example 192.168.0.1')
    sftp_username = fields.Char(
        string='Username on SFTP Server',
        help='''The username where the SFTP connection should be made with.
        This is the user on the external server.''')
    sftp_password = fields.Char(
        string='Password User SFTP Server',
        help='''The password from the user where the SFTP connection should be
              made with. This is the password from the user on the
              external server.''')
    sftp_path = fields.Char(
        string='Path external server',
        help='''The location to the folder where the dumps should be written
             to. For example /odoo/backups/.\nFiles will then be written to
             /odoo/backups/ on your remote server.''')
    sftp_rsa_key_path = fields.Char(
        string='Path rsa key',
        help="The location to the folder where the rsa key is saved. "
             "For example /opt/odoo/.ssh/id_rsa.")

    @api.multi
    def set_values(self):
        super(SaasPortalConfigWizard, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("saas_server.sftp_server", self.sftp_server)
        ICPSudo.set_param("saas_server.sftp_username", self.sftp_username)
        ICPSudo.set_param("saas_server.sftp_password", self.sftp_password)
        ICPSudo.set_param("saas_server.sftp_path", self.sftp_path)
        ICPSudo.set_param("saas_server.sftp_rsa_key_path",
                          self.sftp_rsa_key_path)

    @api.model
    def get_values(self):
        res = super(SaasPortalConfigWizard, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            sftp_server=ICPSudo.get_param('saas_server.sftp_server'),
            sftp_username=ICPSudo.get_param('saas_server.sftp_username'),
            sftp_password=ICPSudo.get_param('saas_server.sftp_password'),
            sftp_path=ICPSudo.get_param('saas_server.sftp_path'),
            sftp_rsa_key_path=ICPSudo.get_param(
                'saas_server.sftp_rsa_key_path'),
        )
        return res

    def test_sftp_connection(self):
        server = self.env["ir.config_parameter"].sudo().get_param(
            "saas_server.sftp_server", default=None)
        username = self.env["ir.config_parameter"].sudo().get_param(
            "saas_server.sftp_username", default=None)
        password = self.env["ir.config_parameter"].sudo().get_param(
            "saas_server.sftp_password", default=None)
        sftp_rsa_key_path = self.env["ir.config_parameter"].sudo().get_param(
            'saas_server.sftp_rsa_key_path')
        sftp_password = self.env["ir.config_parameter"].sudo().get_param(
            'saas_server.sftp_password')
        params = {
            "host": server,
            "username": username,
        }

        try:
            # Connect with external server over SFTP,
            # so we know sure that everything works.
            if sftp_rsa_key_path:
                params["private_key"] = sftp_rsa_key_path
                if password:
                    params["private_key_pass"] = sftp_password
            else:
                params["password"] = password

            with pysftp.Connection(**params):
                raise exceptions.Warning(_("Connection Test Succeeded!"))
        except (pysftp.CredentialException,
                pysftp.ConnectionException,
                pysftp.SSHException):
            _logger.info("Connection Test Failed!", exc_info=True)
            raise exceptions.Warning(_("Connection Test Failed!"))
