# -*- coding: utf-8 -*-
import requests
import werkzeug
import datetime

import openerp
from openerp.addons.saas_utils import connector, database
from openerp.addons.web.http import request
from openerp.tools import config
from openerp import models, fields, api, SUPERUSER_ID
from openerp import http


class SaasConfig(models.TransientModel):
    _name = 'saas.config'

    action = fields.Selection([('edit', 'Edit'), ('upgrade', 'Upgrade'), ('delete', 'Delete')],
                                'Action')
    database_id = fields.Many2one('oauth.application', string='Client')
    server_id = fields.Many2one('saas_portal.server', string='Server')
    update_addons = fields.Char('Update Addons', size=256)
    install_addons = fields.Char('Install Addons', size=256)
    uninstall_addons = fields.Char('Uninstall Addons', size=256)
    fix_ids = fields.One2many('saas.config.fix', 'config_id', 'Fixes')
    description = fields.Text('Result')

    @api.multi
    def execute_action(self):
        res = False
        method = '%s_database' % self.action
        if hasattr(self, method):
            res = getattr(self, method)()
        return res

    @api.multi
    def delete_database(self):
        return self.database_id.delete_database()

    def upgrade_database(self, cr, uid, obj, context=None):
        res = {}
        scheme = request.httprequest.scheme
        payload = {
            'update_addons': obj.update_addons,
            'install_addons': obj.install_addons,
            'uninstall_addons': obj.uninstall_addons,
            'fixes': ','.join(['%s-%s' % (x.model, x.method) for x in obj.fix_ids])
        }


        dbs = obj.database and obj.database.split(',') or database.get_market_dbs(False)
        for db in dbs:
            url = '{scheme}://{domain}/saas_client/upgrade_database'.format(scheme=scheme, domain=db.replace('_', '.'))
            r = requests.post(url, data=payload)
            res[db] = r.status_code
        self.write(cr, uid, obj.id, {'description': str(res)})
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'saas.config',
            'res_id': obj.id,
            'target': 'new'
        }


class SaasConfigFix(models.TransientModel):
    _name = 'saas.config.fix'

    model = fields.Char('Model', required=1, size=64)
    method = fields.Char('Method', required=1, size=64)
    config_id = fields.Many2one('saas.config', 'Config')

class SaasPortalCreateClient(models.TransientModel):
    _name = 'saas_portal.create_client'

    def _default_plan_id(self):
        return self._context.get('active_id')

    def _default_name(self):
        plan_id = self._default_plan_id()
        if plan_id:
            plan = self.env['saas_portal.plan'].browse(plan_id)
            return plan.generate_dbname(raise_error=False)[0]
        return ''

    name = fields.Char('Database name', required=True, default=_default_name)
    plan_id = fields.Many2one('saas_portal.plan', string='Plan', readonly=True, default=_default_plan_id)

    @api.multi
    def apply(self):
        wizard = self[0]
        url = wizard.plan_id._create_new_database(dbname=wizard.name)
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'name': 'Create Client',
            'url': url
        }
