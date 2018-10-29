from odoo import SUPERUSER_ID as SI
from odoo import api
from odoo import exceptions
from odoo import models, fields
from odoo.tools.translate import _
from odoo.addons.saas_base.exceptions import SuspendedDBException


class ResUsers(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    oauth_provider_id = fields.Many2one('auth.oauth.provider', default=lambda self: self.env.ref('saas_client.saas_oauth_provider').id)

    @api.model
    def create(self, vals):
        max_users = self.env["ir.config_parameter"].sudo().get_param("saas_client.max_users")
        max_users = int(max_users)
        if max_users:
            cur_users = self.env['res.users'].search_count([('share', '=', False), ('id', '!=', SI)])
            if cur_users >= max_users:
                raise exceptions.Warning(_('Maximum allowed users is %(max_users)s, while you already have %(cur_users)s') % {'max_users': max_users, 'cur_users': cur_users})
        return super(ResUsers, self).create(vals)

    @classmethod
    def check(cls, db, uid, passwd):
        res = super(ResUsers, cls).check(db, uid, passwd)
        cr = cls.pool.cursor()
        try:
            self = api.Environment(cr, uid, {})[cls._name]
            suspended = self.env['ir.config_parameter'].sudo().get_param('saas_client.suspended', '0')
            if suspended == "1" and uid != SI:
                raise SuspendedDBException
        finally:
            cr.close()
        return res
