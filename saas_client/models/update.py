# -*- coding: utf-8 -*-
from odoo.models import AbstractModel
from odoo.tools.config import config


class publisher_warranty_contract(AbstractModel):
    _inherit = "publisher_warranty.contract"

    def update_notification(self, cron_mode=True):
        url = self.env['ir.config_parameter'].get_param('saas_client.publisher_warranty_url')
        print 'update_notification', url
        if not url:
            return
        config.options["publisher_warranty_url"] = url

        return super(publisher_warranty_contract, self).update_notification(cron_mode)
