import os
import time
from datetime import datetime
import base64
import openerp
from openerp import api, models, fields, SUPERUSER_ID, exceptions
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import psycopg2
import random
import string
from openerp.service import db
import logging
_logger = logging.getLogger(__name__)


class SaasServerClient(models.Model):
    _inherit = 'saas_server.client'
    
    @api.model
    def _transport_backup(self, db_dump):
        '''
        backup transport agents should override this        
        '''
        raise exceptions.Warning('Transport agent has not been configured')

    @api.one
    def backup_database(self):
        data = {}
        try:
            db_dump = base64.b64decode(db.exp_dump(self.name))
            filename = "%(db_name)s %(timestamp)s.zip" % {
            'db_name': self.name,
            'timestamp': datetime.utcnow().strftime(
                "%Y-%m-%d_%H-%M-%SZ")
            }
            self._transport_backup(db_dump, filename=filename)
            data['status'] = 'success'
        except Exception, e:
            _logger.exception('An error happened during database %s backup' %(self.name))
            data['status'] = 'fail'
            data['message'] = str(e)
        return data
