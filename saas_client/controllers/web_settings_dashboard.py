# -*- coding: utf-8 -*-
import openerp
from openerp import http
from openerp.http import request
from openerp.addons.web_settings_dashboard.controllers.main import WebSettingsDashboard
from openerp.addons.saas_base.tools import get_size


class SaaSWebSettingsDashboard(WebSettingsDashboard):

    @http.route('/web_settings_dashboard/data', type='json', auth='user')
    def web_settings_dashboard_data(self, **kw):

        result = super(SaaSWebSettingsDashboard, self).web_settings_dashboard_data(**kw)

        cur_users = request.env['res.users'].search_count([('share', '=', False)])
        max_users = request.env['ir.config_parameter'].get_param('saas_client.max_users', default='')
        expiration_datetime = request.env['ir.config_parameter'].get_param('saas_client.expiration_datetime', default='')
        pay_subscription_url = request.env['ir.config_parameter'].get_param('saas_client.pay_subscription_url', default='').strip()

        data_dir = openerp.tools.config['data_dir']

        file_storage = get_size('%s/filestore/%s' % (data_dir, request.env.cr.dbname))
        file_storage = int(file_storage / (1024 * 1024))

        request.env.cr.execute("select pg_database_size('%s')" % request.env.cr.dbname)
        db_storage = request.env.cr.fetchone()[0]
        db_storage = int(db_storage / (1024 * 1024))

        result.update({'saas': {'cur_users': cur_users,
                                'max_users': max_users,
                                'expiration_datetime': expiration_datetime,
                                'file_storage': file_storage,
                                'db_storage': db_storage,
                                'pay_subscription_url': pay_subscription_url}})

        return result
