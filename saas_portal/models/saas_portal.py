# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api, SUPERUSER_ID
from openerp.addons.saas_utils import connector, database
from openerp import http
from openerp.tools import config


class SaasPortalPlan(models.Model):
    _name = 'saas_portal.plan'

    name = fields.Char('Plan')
    template = fields.Char('Template')
    demo = fields.Boolean('Demo Data')
    sequence = fields.Integer('Sequence')
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')],
                             'State', default='draft')
    role_id = fields.Many2one('saas_server.role', 'Role')
    required_addons_ids = fields.Many2many('ir.module.module',
                                           rel='company_required_addons_rel',
                                           id1='company_id', id2='module_id',
                                           string='Required Addons')
    optional_addons_ids = fields.Many2many('ir.module.module',
                                           rel='company_optional_addons_rel',
                                           id1='company_id', id2='module_id',
                                           string='Optional Addons')

    _order = 'sequence'

    def create_template(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        openerp.service.db.exp_create_database(obj.template, obj.demo, 'en_US')
        addon_names = [x.name for x in obj.required_addons_ids]
        if 'saas_client' not in addon_names:
            addon_names.append('saas_client')
        to_search = [('name', 'in', addon_names)]
        addon_ids = connector.call(obj.template, 'ir.module.module',
                                   'search', to_search)
        for addon_id in addon_ids:
            connector.call(obj.template, 'ir.module.module',
                           'button_immediate_install', addon_id)
        return self.write(cr, uid, obj.id, {'state': 'confirmed'})

    def edit_template(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        d = config.get('local_url')
        url = '%s/login?db=%s&login=admin&key=admin' % (d, obj.template)
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'name': 'Edit Template',
            'url': url
        }

    def upgrade_template(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'saas.config',
            'target': 'new',
            'context': {
                'default_action': 'upgrade',
                'default_database': obj.template
            }
        }

    def delete_template(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        openerp.service.db.exp_drop(obj.template)
        return self.write(cr, uid, obj.id, {'state': 'draft'})


class SaasServerRole(models.Model):
    _name = 'saas_server.role'

    name = fields.Char('Name', size=64)
    code = fields.Char('Code', size=64)


class OauthApplication(models.Model):
    _inherit = 'oauth.application'

    name = fields.Char('Database name', readonly=True)
    client_id = fields.Char('Client ID', readonly=True, select=True)
    users_len = fields.Integer('Count users', readonly=True)
    file_storage = fields.Integer('File storage (MB)', readonly=True)
    db_storage = fields.Integer('DB storage (MB)', readonly=True)
    server = fields.Char('Server', readonly=True)
    plan = fields.Char(compute='_get_plan', string='Plan', size=64)

    def edit_db(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'saas.config',
            'target': 'new',
            'context': {
                'default_action': 'edit',
                'default_database': obj.name
            }
        }

    def upgrade_db(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'saas.config',
            'target': 'new',
            'context': {
                'default_action': 'upgrade',
                'default_database': obj.name
            }
        }

    def unlink(self, cr, uid, ids, context=None):
        user_model = self.pool.get('res.users')
        token_model = self.pool.get('oauth.access_token')
        for obj in self.browse(cr, uid, ids):
            to_search1 = [('application_id', '=', obj.id)]
            tk_ids = token_model.search(cr, uid, to_search1, context=context)
            if tk_ids:
                token_model.unlink(cr, uid, tk_ids)
            to_search2 = [('database', '=', obj.name)]
            user_ids = user_model.search(cr, uid, to_search2, context=context)
            if user_ids:
                user_model.unlink(cr, uid, user_ids)
            openerp.service.db.exp_drop(obj.name)
        return super(OauthApplication, self).unlink(cr, uid, ids, context)

    @api.one
    def _get_plan(self):
        oat = self.pool.get('oauth.access_token')
        to_search = [('application_id', '=', self.id)]
        access_token_ids = oat.search(self.env.cr, self.env.uid, to_search)
        if access_token_ids:
            access_token = oat.browse(self.env.cr, self.env.uid,
                                      access_token_ids[0])
            self.plan = access_token.user_id.plan_id.name


class ResUsers(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    plan_id = fields.Many2one('saas_portal.plan', 'Plan')
    organization = fields.Char('Organization', size=64)
    database = fields.Char('Database', size=64)
