# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010, 2014 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
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
                raise exceptions.Warning(_('Maximimum allowed users is %(max_users)s, while you already have %(cur_users)s') % {'max_users': max_users, 'cur_users': cur_users})
        return super(ResUsers, self).create(vals)

    @classmethod
    def check(cls, db, uid, passwd):
        res = super(ResUsers, cls).check(db, uid, passwd)
        cr = cls.pool.cursor()
        try:
            self = api.Environment(cr, uid, {})[cls._name]
            suspended = self.env['ir.config_parameter'].get_param('saas_client.suspended', '0')
            if suspended == "1" and uid != SI:
                raise SuspendedDBException
        finally:
            cr.close()
        return res
