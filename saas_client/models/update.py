from openerp.models import AbstractModel
from openerp.tools.config import config

class publisher_warranty_contract(AbstractModel):
    _inherit = "publisher_warranty.contract"

    def update_notification(self, cr, uid, ids, cron_mode=True, context=None):
        url = self.pool['ir.config_parameter'].get_param(cr, uid, 'saas_client.publisher_warranty_url')
        print 'update_notification', url
        if not url:
            return
        config.options["publisher_warranty_url"] = url

        return super(publisher_warranty_contract, self).update_notification(cr, uid, ids, cron_mode, context)
