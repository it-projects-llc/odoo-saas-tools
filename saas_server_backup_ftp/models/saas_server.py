# -*- coding: utf-8 -*-
import tempfile
from openerp import api, models
import logging
_logger = logging.getLogger(__name__)
try:
    import pysftp
except ImportError:
    _logger.critical('saas_server_backup_ftp requires the python library pysftp which is not found on your installation')


class SaasServerClient(models.Model):
    _inherit = 'saas_server.client'

    @api.model
    def _transport_backup(self, dump_db, filename=None):
        server = self.env['ir.config_parameter'].get_param('saas_server.sftp_server', None)
        username = self.env['ir.config_parameter'].get_param('saas_server.sftp_username', None)
        password = self.env['ir.config_parameter'].get_param('saas_server.sftp_password', None)
        path = self.env['ir.config_parameter'].get_param('saas_server.sftp_path', None)

        srv = pysftp.Connection(host=server, username=username, password=password)
        #set keepalive to prevent socket closed / connection dropped error
        srv._transport.set_keepalive(30)

        try:
            srv.chdir(path)
        except IOError:
            #Create directory and subdirs if they do not exist.
            currentDir = ''
            for dirElement in path.split('/'):
                currentDir += dirElement + '/'
                try:
                    srv.chdir(currentDir)
                except:
                    print('(Part of the) path didn\'t exist. Creating it now at ' + currentDir)
                    # Make directory and then navigate into it
                    srv.mkdir(currentDir, mode=777)
                    srv.chdir(currentDir)
                    pass

        srv.chdir(path)
        with tempfile.TemporaryFile() as t:
            dump_db(t)
            t.seek(0)
            srv.putfo(t, filename)
        srv.close()

    @api.model
    def schedule_saas_databases_backup(self):
        self.search([('state', '!=', 'deleted')]).backup_database()
