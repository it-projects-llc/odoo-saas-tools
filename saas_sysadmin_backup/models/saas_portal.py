import urllib2
import simplejson
import werkzeug
import requests

from openerp import models, fields, api
from openerp.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)


class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'
    
    backup = fields.Boolean('Backup on Modify', help="Backs up first before deleting \
                            or upgrading", default=True)
    
    @api.multi 
    def action_backup(self):
        '''
        call to backup database
        '''
        self.ensure_one()
        if not self[0].backup:
            return
        state = {
            'd': self.name,
            'client_id': self.client_id,
        }

        url = self.server_id._request_server(path='/saas_server/backup_database', state=state, client_id=self.client_id)[0]
        res = requests.get(url, verify=(self.server_id.request_scheme == 'https' and self.server_id.verify_ssl))
        _logger.info('delete database: %s', res.text)
        if res.ok != True:
            raise Warning('Reason: %s \n Message: %s' % (res.reason, res.content))
        data = simplejson.loads(res.text)
        if data[0]['status'] != 'success':
            warning = data[0].get('message', 'Could not backup database; please check your logs')
            raise Warning(warning)
        return True
    
    @api.multi
    def delete_database(self):
        self.action_backup()
        return super(SaasPortalClient, self).delete_database()
    
 
    @api.multi
    def upgrade_database(self):
        self.action_backup()
        return super(SaasPortalClient, self).upgrade_database()
