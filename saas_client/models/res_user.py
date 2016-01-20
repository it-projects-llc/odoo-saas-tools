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
from openerp import models, fields, api, SUPERUSER_ID as SI, exceptions
from openerp.tools.translate import _
from openerp.addons.saas_base.exceptions import SuspendedDBException


class ResUsers(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    _defaults = {
        'oauth_provider_id': lambda self,cr,uid,ctx=None: self.pool['ir.model.data'].xmlid_to_res_id(cr, SI, 'saas_server.saas_oauth_provider')
    }
    @api.model
    def create(self, vals):
        max_users = self.env["ir.config_parameter"].sudo().get_param("saas_client.max_users")
        if max_users:
            max_users = int(max_users)
            cur_users = self.env['res.users'].search_count([('share', '=', False)])
            if cur_users >= max_users:
                raise exceptions.Warning(_('Maximimum allowed users is %(max_users)s, while you already have %(cur_users)s') % {'max_users':max_users, 'cur_users': cur_users})
        return super(ResUsers, self).create(vals)

    def check(self, db, uid, passwd):
        res = super(ResUsers, self).check(db, uid, passwd)
        suspended = self.pool['ir.config_parameter'].get_saas_client_parameters(db)
        if suspended == "1" and uid != SI:
            raise SuspendedDBException
        return res
