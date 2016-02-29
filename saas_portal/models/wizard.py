# -*- coding: utf-8 -*-
import requests
import werkzeug
import datetime
import simplejson

import openerp
from openerp.addons.saas_utils import connector, database
from openerp.addons.web.http import request
from openerp.tools import config
from openerp import models, fields, api, SUPERUSER_ID
from openerp import http


class SaasConfig(models.TransientModel):
    _name = 'saas.config'

    def _default_database_ids(self):
        return self._context.get('active_ids')

    action = fields.Selection([('edit', 'Edit'), ('upgrade', 'Configure'), ('delete', 'Delete')],
                                'Action')
    database_ids = fields.Many2many('saas_portal.client', string='Database', default=_default_database_ids)
    update_addons_list = fields.Boolean('Update Addon List', default=True)
    update_addons = fields.Char('Update Addons', size=256)
    install_addons = fields.Char('Install Addons', size=256)
    uninstall_addons = fields.Char('Uninstall Addons', size=256)
    access_owner_add = fields.Char('Grant access to Owner')
    access_remove = fields.Char('Restrict access', help='Restrict access for all users except super-user.\nNote, that ')
    fix_ids = fields.One2many('saas.config.fix', 'config_id', 'Fixes')
    param_ids = fields.One2many('saas.config.param', 'config_id', 'Parameters')
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
        return self.database_ids.delete_database()

    @api.multi
    def upgrade_database(self):
        self.ensure_one()
        obj = self[0]
        scheme = request.httprequest.scheme
        payload = {
            'update_addons_list': (obj.update_addons_list or ''),
            'update_addons': obj.update_addons.split(',') if obj.update_addons else [],
            'install_addons': obj.install_addons.split(',') if obj.install_addons else [],
            'uninstall_addons': obj.uninstall_addons.split(',') if obj.uninstall_addons else [],
            'access_owner_add': obj.access_owner_add.split(',') if obj.access_owner_add else [],
            'access_remove': obj.access_remove.split(',') if obj.access_remove else [],
            'fixes': [[x.model, x.method] for x in obj.fix_ids],
            'params': [{'key': x.key, 'value': x.value, 'hidden': x.hidden} for x in obj.param_ids],
        }
        res = self.database_ids.upgrade(payload=payload)

        res_str = '\n\n'.join(res)
        obj.write({'description': res_str})
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'saas.config',
            'res_id': obj.id,
            'target': 'new'
        }

    @api.model
    def do_upgrade_database(self, payload, saas_portal_client_id):
        client = self.env['saas_portal.client'].browse(saas_portal_client_id)
        state = {
            'data': payload,
        }
        url = client.server_id._request_server(
            path='/saas_server/upgrade_database',
            client_id=client.client_id,
            state=state,
        )[0]
        res = requests.get(url, verify=(client.server_id.request_scheme == 'https' and client.server_id.verify_ssl))
        if res.ok != True:
            raise Warning('Reason: %s \n Message: %s' % (res.reason, res.content))
        return res.text

class SaasConfigFix(models.TransientModel):
    _name = 'saas.config.fix'

    model = fields.Char('Model', required=1, size=64)
    method = fields.Char('Method', required=1, size=64)
    config_id = fields.Many2one('saas.config', 'Config')

class SaasConfigParam(models.TransientModel):
    _name = 'saas.config.param'

    def _get_keys(self):
        return [
            ('saas_client.max_users', 'Max Users'),
            ('saas_client.suspended', 'Suspended'),
            ('saas_client.total_storage_limit', 'Total storage limit'),
        ]

    key = fields.Selection(selection=_get_keys, string='Key', required=1, size=64)
    value = fields.Char('Value', required=1, size=64)
    config_id = fields.Many2one('saas.config', 'Config')
    hidden = fields.Boolean('Hidden parameter', default=True)

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
    partner_id = fields.Many2one('res.partner', string='Partner')
    user_id = fields.Many2one('res.users', string='User')
    notify_user = fields.Boolean(help='Notify user by email when database will have been created', default=False)
    support_team_id = fields.Many2one('saas_portal.support_team', 'Support Team', default=lambda self: self.env.user.support_team_id)
    async_creation = fields.Boolean('Asynchronous', default=False, help='Asynchronous creation of client base')

    @api.onchange('user_id')
    def update_partner(self):
        if self.user_id:
            self.partner_id = self.user_id.partner_id

    @api.multi
    def apply(self):
        wizard = self[0]
        res = wizard.plan_id.create_new_database(dbname=wizard.name, partner_id=wizard.partner_id.id, user_id=self.user_id.id,
                                                 notify_user=self.notify_user,
                                                 support_team_id=self.support_team_id.id,
                                                 async=self.async_creation)
        if self.async_creation:
            return
        client = self.env['saas_portal.client'].browse(res.get('id'))
        client.server_id.action_sync_server()
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'saas_portal.client',
            'res_id': client.id,
            'target': 'current',
        }


class SaasPortalDuplicateClient(models.TransientModel):
    _name = 'saas_portal.duplicate_client'

    def _default_client_id(self):
        return self._context.get('active_id')

    def _default_partner(self):
        client_id = self._default_client_id()
        if client_id:
            client = self.env['saas_portal.client'].browse(client_id)
            return client.partner_id
        return ''
    
    def _default_expiration(self):
        client_id = self._default_client_id()
        if client_id:
            client = self.env['saas_portal.client'].browse(client_id)
            return client.plan_id.expiration
        return ''

    name = fields.Char('Database Name', required=True)
    client_id = fields.Many2one('saas_portal.client', string='Base Client', readonly=True, default=_default_client_id)
    expiration = fields.Integer('Expiration', default=_default_expiration)
    partner_id = fields.Many2one('res.partner', string='Partner', default=_default_partner)

    @api.multi
    def apply(self):
        self.ensure_one()
        res = self.client_id.duplicate_database(
            dbname=self.name, partner_id=self.partner_id.id, expiration=None)
        client = self.env['saas_portal.client'].browse(res.get('id'))
        client.server_id.action_sync_server()
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'saas_portal.client',
            'res_id': client.id,
            'target': 'current',
        }


class SaasPortalRenameDatabase(models.TransientModel):
    _name = 'saas_portal.rename_database'

    def _default_client_id(self):
        return self._context.get('active_id')

    name = fields.Char('New Name', required=True)
    client_id = fields.Many2one('saas_portal.client', string='Base Client', readonly=True, default=_default_client_id)

    @api.multi
    def apply(self):
        self.ensure_one()
        self.client_id.rename_database(new_dbname=self.name)
        return {
            'type': 'ir.actions.act_window_close',
        }
