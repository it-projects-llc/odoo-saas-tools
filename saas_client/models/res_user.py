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
import openerp
from openerp import models, fields, api, SUPERUSER_ID as SI, exceptions
from openerp.tools import config
from openerp.tools.translate import _
from openerp.addons.saas_utils import connector


class ResUsers(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        max_users = self.env["ir.config_parameter"].get_param("saas_client.max_users")
        if max_users:
            max_users = int(max_users)
            cur_users = self.env['res.users'].search_count([('share', '=', False)])
            if cur_users >= max_users:
                raise exceptions.Warning(_('Maximimum allowed users is %(max_users)s, while you already have %(cur_users)s') % {'max_users':max_users, 'cur_users': cur_users})
        return super(ResUsers, self).create(vals)


    available_addons_ids = fields.Many2many(compute='_compute_addons',
                                            comodel_name='ir.module.module',
                                            string='Available Addons')

    @api.one
    def _compute_addons(self):
        addon_ids = []
        add_names = []
        login = self.login
        db = config.get('db_master')
        registry = openerp.modules.registry.RegistryManager.get(db)
        with registry.cursor() as cr:
            ru = registry['res.users']
            user_ids = ru.search(cr, SI, [('login', '=', login)])
            if user_ids:
                user = ru.browse(cr, SI, user_ids[0])
                add_names = [x.name for x in user.plan_id.optional_addons_ids]
        if add_names:
            imm = self.env['ir.module.module']
            addons = imm.search([('name', 'in', add_names)])
            dependencies = []
            for addon in addons:
                dependencies += self._get_dependencies(addon)
            addon_ids = list(set([x.id for x in addons] + dependencies))
        self.available_addons_ids = addon_ids

    def _get_dependencies(self, addon):
        dependencies = []
        for dep in addon.dependencies_id:
            dependencies.append(dep.depend_id.id)
            dependencies += self._get_dependencies(dep.depend_id)
        return dependencies
