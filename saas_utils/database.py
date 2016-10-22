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
from odoo import http, SUPERUSER_ID as SI
from odoo.http import request


def get_market_dbs(with_templates=True):
    dbs = []
    if with_templates:
        sp = request.registry.get('saas_portal.plan')
        data = sp.search_read(request.cr, SI, [('state', '=', 'confirmed')],
                              ['template'])
        dbs += [d['template'] for d in data]
    icp = request.registry.get('ir.config_parameter')
    bd = icp.get_param(request.cr, SI, 'saas_portal.base_saas_domain')
    dbs += [db for db in http.db_list(force=True)
            if db.endswith('_%s' % bd.replace('.', '_'))]
    return dbs
