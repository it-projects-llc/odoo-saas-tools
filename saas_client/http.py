import odoo
from . import ADMINUSER_ID
from odoo.http import OpenERPSession
from odoo.addons.base_sparse_field.models.fields import monkey_patch
from odoo.addons.saas_base.exceptions import SuspendedDBException


@monkey_patch(OpenERPSession)
def check_security(self):
    with odoo.registry(self.db).cursor() as cr:
        uid = self.uid
        env = odoo.api.Environment(cr, uid, {})
        suspended = env['ir.config_parameter'].sudo().get_param('saas_client.suspended', '0')
        if suspended == "1" and uid not in (odoo.SUPERUSER_ID, ADMINUSER_ID):
            raise SuspendedDBException
    return check_security.super(self)

