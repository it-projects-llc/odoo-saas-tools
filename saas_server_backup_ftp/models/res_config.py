# -*- coding: utf-8 -*-
from openerp import models, fields
from openerp import tools, _
from openerp.osv import osv
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
    def get_default_sftp_rsa_key_path(self, cr, uid, ids, context=None):
        sftp_rsa_key_path = self.pool.get("ir.config_parameter").get_param(
            cr, uid, "saas_server.sftp_rsa_key_path", default=None,
            context=context)
        return {'sftp_rsa_key_path': sftp_rsa_key_path or False}

    def set_sftp_rsa_key_path(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid,
                                        "saas_server.sftp_rsa_key_path",
                                        record.sftp_rsa_key_path or '',
                                        context=context)
    # sftp_server
    def get_default_sftp_server(self, cr, uid, ids, context=None):
        sftp_server = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_server.sftp_server", default=None, context=context)
        return {'sftp_server': sftp_server or False}

    def set_sftp_server(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "saas_server.sftp_server", record.sftp_server or '', context=context)

    # sftp_username
    def get_default_sftp_username(self, cr, uid, ids, context=None):
        sftp_username = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_server.sftp_username", default=None, context=context)
        return {'sftp_username': sftp_username or False}

    def set_sftp_username(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "saas_server.sftp_username", record.sftp_username or '', context=context)

    # sftp_password
    def get_default_sftp_password(self, cr, uid, ids, context=None):
        sftp_password = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_server.sftp_password", default=None, context=context)
        return {'sftp_password': sftp_password or False}

    def set_sftp_password(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "saas_server.sftp_password", record.sftp_password or '', context=context)

    # sftp_path
    def get_default_sftp_path(self, cr, uid, ids, context=None):
        sftp_path = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_server.sftp_path", default=None, context=context)
        return {'sftp_path': sftp_path or False}

    def set_sftp_path(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "saas_server.sftp_path", record.sftp_path or '', context=context)

    def test_sftp_connection(self, cr, uid, ids, context=None):
        server = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_server.sftp_server", default=None, context=context)
        username = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_server.sftp_username", default=None, context=context)
        password = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_server.sftp_password", default=None, context=context)
        path = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_server.sftp_path", default=None, context=context)
        sftp_rsa_key_path = self.env['ir.config_parameter'].get_param(
            'saas_server.sftp_rsa_key_path', None)

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
            messageTitle = "Connection Test Failed!"
            messageContent += "Here is what we got instead:\n"
        if "Failed" in messageTitle:
            raise osv.except_osv(_(messageTitle), _(messageContent + "%s") % tools.ustr(e))
        else:
            raise osv.except_osv(_(messageTitle), _(messageContent))
