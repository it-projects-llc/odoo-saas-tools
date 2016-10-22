# -*- coding: utf-8 -*-
import odoo
from odoo import http, SUPERUSER_ID
from odoo.http import request
from odoo.addons.web_settings_dashboard.controllers.main import WebSettingsDashboard
from odoo.addons.saas_base.tools import get_size
import pytz
from pytz import timezone
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SaaSWebSettingsDashboard(WebSettingsDashboard):

    @http.route('/web_settings_dashboard/data', type='json', auth='user')
    def web_settings_dashboard_data(self, **kw):

        result = super(SaaSWebSettingsDashboard, self).web_settings_dashboard_data(**kw)

        uid = request.session.uid
        user_obj = request.env['res.users'].sudo().browse(uid)
        cur_users = request.env['res.users'].search_count([('share', '=', False), ('id', '!=', SUPERUSER_ID)])
        max_users = request.env['ir.config_parameter'].sudo().get_param('saas_client.max_users', default='')
        expiration_datetime = request.env['ir.config_parameter'].sudo().get_param('saas_client.expiration_datetime', default='').strip()
        datetime_obj = expiration_datetime and datetime.strptime(expiration_datetime, DEFAULT_SERVER_DATETIME_FORMAT)
        pay_subscription_url = request.env['ir.config_parameter'].sudo().get_param('saas_client.pay_subscription_url', default='').strip()
        if datetime_obj and user_obj.tz:
            user_timezone = timezone(user_obj.tz)
            datetime_obj = pytz.utc.localize(datetime_obj)
            datetime_obj = datetime_obj.astimezone(user_timezone)
        data_dir = odoo.tools.config['data_dir']

        file_storage = get_size('%s/filestore/%s' % (data_dir, request.env.cr.dbname))
        file_storage = int(file_storage / (1024 * 1024))

        request.env.cr.execute("select pg_database_size('%s')" % request.env.cr.dbname)
        db_storage = request.env.cr.fetchone()[0]
        db_storage = int(db_storage / (1024 * 1024))

        result.update({'saas': {'cur_users': cur_users,
                                'max_users': max_users,
                                'expiration_datetime': datetime_obj and datetime_obj.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                'file_storage': file_storage,
                                'db_storage': db_storage,
                                'pay_subscription_url': pay_subscription_url}})

        return result
