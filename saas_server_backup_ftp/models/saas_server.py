# -*- coding: utf-8 -*-
import tempfile
from openerp import api, models
import xmlrpclib
import socket
try:
    import pysftp
except ImportError:
    raise ImportError('This module needs pysftp to automaticly write backups to the FTP through SFTP. Please install pysftp on your system. (sudo pip install pysftp)')

import logging
_logger = logging.getLogger(__name__)


class SaasServerClient(models.Model):
    _inherit = 'saas_server.client'

    @api.multi
    def _check_db_exist(self):
        # TODO: should we use this function somehow?
        conn = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/db')
        try:
            db_list = conn.list()
        except socket.error,e:
            raise e

        for rec in self:
            if rec.name in db_list:
                return True
        return False

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
        self.search([]).backup_database()
