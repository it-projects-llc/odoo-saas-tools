# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request
from openerp.addons.web_settings_dashboard.controllers.main import WebSettingsDashboard


class SaaSWebSettingsDashboard(WebSettingsDashboard):

    @http.route('/web_settings_dashboard/data', type='json', auth='user')
    def web_settings_dashboard_data(self, **kw):

        result = super(SaaSWebSettingsDashboard, self).web_settings_dashboard_data(**kw)

        cur_users = request.env['res.users'].search_count([('share', '=', False)])
        max_users = request.env['ir.config_parameter'].get_param('saas_client.max_users', default='')
        expiration_datetime = request.env['ir.config_parameter'].get_param('saas_client.expiration_datetime', default='')

        result.update({'saas': {'cur_users': cur_users, 'max_users': max_users, 'expiration_datetime': expiration_datetime}})

        return result
