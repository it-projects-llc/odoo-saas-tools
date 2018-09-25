# -*- coding: utf-8 -*-
import requests
import xmlrpclib

from odoo import models, fields, api
from odoo import SUPERUSER_ID as SI


class SaasPortalServer(models.Model):
    _inherit = 'saas_portal.server'

    @api.multi
    def _get_xmlrpc_object(self, db_name):
        self.ensure_one()

        url = self.local_request_scheme + '://' + self.local_host
        if self.local_port:
            url += ':' + self.local_port
        db = db_name
        username = 'admin'
        password = self.password
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})

        return db, uid, password, xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

    @api.multi
    def _get_odoo_version(self):
        self.ensure_one()
        db, uid, password, models = self._get_xmlrpc_object(self.name)
        ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search',
                                [[['name', '=', 'base']]],
                                )
        base_module = models.execute_kw(db, uid, password,
                                    'ir.module.module',
                                    'read', [ids],
                                    {'fields': ['latest_version']})
        return base_module[0].get('latest_version')

    def _prepare_module(self, module, plan):
        attachment_name = 'addon_{0}_{1}.{2}'.format(self.odoo_version,
                                                     module['name'],
                                                     self.env['ir.config_parameter'].get_param('saas_portal.base_saas_domain'))
        ir_attachment = self.env['ir.attachment'].create({'name': attachment_name, 'type': 'binary', 'db_datas': module.get('icon_image')})
        return {
            'technical_name': module.get('name'),
            'demo_plan_id': plan.id,
            'shortdesc': module.get('shortdesc'),
            'author': module.get('author'),
            'icon_attachment_id': ir_attachment.id,
            'icon': module.get('icon_image'),
            'summary': module.get('summary'),
            'price': module.get('price'),
            'currency': module.get('currency'),
        }

    @api.multi
    def _create_demo_plan(self, demo_module):
        self.ensure_one()

        if not demo_module.get('installable', True):
            return None

        template_obj = self.env['saas_portal.database']
        plan_obj = self.env['saas_portal.plan']
        if not self.odoo_version:
            version = self._get_odoo_version()
            if version:
                self.odoo_version = version.split('.', 1)[0]
        namestring = '{0}-{1}'
        saas_domain = self.env['ir.config_parameter'].get_param('saas_portal.base_saas_domain')
        template_name = namestring.format(demo_module['demo_url'], 't')
        plan_name = 'Demo for {0}.0 {1}'.format(self.odoo_version, demo_module['demo_url'])

        if template_obj.search_count([('name', '=', template_name), ('server_id', '=', self.id)]) == 0:
            template = template_obj.create({'name': template_name, 'server_id': self.id})
            if plan_obj.search_count([('name', '=', plan_name)]) == 0:
                plan = plan_obj.create({'name': plan_name,
                                        'server_id': self.id,
                                        'dbname_template': namestring.format(demo_module['demo_url'], '%i'),
                                        'template_id': template.id,
                                        'on_create_email_template': self.env.ref('saas_portal_demo.email_template_create_saas_for_demo').id,
                                        'expiration': 48,
                                        'demo': True,
                                        })
                return plan
        else:
            return None


    @api.multi
    def _create_demo_images(self, demo_module):
        self.ensure_one()

        db, uid, password, models = self._get_xmlrpc_object(self.name)

        images = models.execute_kw(db, uid, password, 'ir.module.module', 'get_demo_images', [demo_module['id']])

        return images


    @api.multi
    def _create_demo_product(self, demo_module, plan):
        self.ensure_one()

        product_template_obj = self.env['product.template']
        product_product_obj = self.env['product.product']
        product_attribute_line_obj = self.env['product.attribute.line']

        product_template_name = demo_module['demo_title']
        product_template = product_template_obj.search([('module_name', '=', demo_module['name'])], limit=1)

        odoo_version_attrib = self.env.ref('saas_portal_demo.odoo_version_product_attribute')
        attrib_value = self.env.ref('saas_portal_demo.product_attribute_value_{}'.format(self.odoo_version))

        images_res = self._create_demo_images(demo_module)

        if not product_template:
            vals = {
                'name': product_template_name,
                'module_name': demo_module['name'],
                'website_published': True,
                'seo_url': demo_module.get('demo_url'),
                'description': demo_module.get('demo_summary'),
                'image': images_res and images_res.pop(0)[1] or None,
                'sale_on_website': False,
                'saas_demo': True,
                'type': 'service',
                'product_image_ids': images_res and [(0, 0, {'name': name, 'image': image}) for name, image in images_res] or None,
            }
            product_template = product_template_obj.with_context({
                'create_product_product': False
            }).create(vals)

        product_attribute_line = product_attribute_line_obj.search([
            ('product_tmpl_id', '=', product_template.id),
            ('attribute_id', '=', odoo_version_attrib.id),
        ], limit=1)

        if not product_attribute_line:
            product_attribute_line = product_attribute_line_obj.create({'product_tmpl_id': product_template.id,
                                                                        'attribute_id': odoo_version_attrib.id,
                                                                        'value_ids': [(4, attrib_value.id, 0)],
                                                                        })
        elif not product_attribute_line.value_ids.filtered(lambda r: r.id == attrib_value.id):
            product_attribute_line.update({'value_ids': [(4, attrib_value.id, 0)]})

        product_product = product_product_obj.create({
            'product_tmpl_id': product_template.id,
            'attribute_value_ids': [(4, attrib_value.id)],
            'variant_plan_id': plan.id,
        })

    @api.multi
    def generate_demo_plans(self):
        demo_plan_module_obj = self.env['saas_portal.demo_plan_module']
        demo_plan_hidden_module_obj = self.env['saas_portal.hidden_demo_plan_module']
        for record in self:
            db, uid, password, models = record._get_xmlrpc_object(record.name)
            ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search',
                                    [[['demo_url', '!=', False]]],
                                    )
            modules = models.execute_kw(db, uid, password, 'ir.module.module', 'read', [ids])
            for module in modules:
                plan = record._create_demo_plan(module)

                if not plan:
                    continue

                vals = record._prepare_module(module, plan)
                demo_plan_module_obj.create(vals)
                record._create_demo_product(module, plan)
                if module.get('demo_addons'):
                    ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search',
                                            [[['name', 'in', module['demo_addons'].split(',')]]],
                                            {'limit': 10})
                    addon_modules = models.execute_kw(db, uid, password, 'ir.module.module', 'read', [ids])
                    for addon in addon_modules:
                        vals = record._prepare_module(addon, plan)
                        demo_plan_module_obj.create(vals)
                if module.get('demo_addons_hidden'):
                    for addon in module['demo_addons_hidden'].split(','):
                        demo_plan_hidden_module_obj.create({'technical_name': addon, 'demo_plan_id': plan.id})

        return True

    @api.multi
    def create_demo_templates(self):
        plan_obj = self.env['saas_portal.plan']
        for record in self:
            demo_plan_ids = plan_obj.search([('server_id', '=', record.id), ('template_id.state', '=', 'draft')])
            for plan in demo_plan_ids:
                plan.with_context({'skip_sync_server': True}).create_template()
                addons = plan.demo_plan_module_ids.mapped('technical_name')
                addons.extend(plan.demo_plan_hidden_module_ids.mapped('technical_name'))
                payload = {'install_addons': addons}
                plan.template_id.upgrade(payload=payload)
                record.action_sync_server()

                # after installing demo modules: make `owner_template` user a member of all the admin's security groups
                db, uid, password, models = plan.template_id._get_xmlrpc_object()
                admin_groups = models.execute_kw(db, uid, password,
                        'res.users', 'search_read',
                        [[['id', '=', SI]]],
                        {'fields': ['groups_id']})
                owner_user_id = models.execute_kw(db, uid, password,
                        'res.users', 'search',
                        [[['login', '=', 'owner_template']]])
                models.execute_kw(db, uid, password,
                        'res.users', 'write',
                        [owner_user_id, {'groups_id': [(6, 0, admin_groups[0]['groups_id'])]}])
                # configure outgoing mail service for using `postfix` docker container
                mail_server_id = models.execute_kw(db, uid, password,
                        'ir.mail_server', 'search', [[]], {'limit': 1})
                models.execute_kw(db, uid, password,
                        'ir.mail_server', 'write', [mail_server_id, {'name': 'postfix', 'smtp_host': 'postfix'}])

        return True

    @api.multi
    def update_repositories(self):
        for record in self:
            db, uid, password, models = record._get_xmlrpc_object(record.name)
            ids = models.execute_kw(db, uid, password, 'saas_server.repository', 'search', [[]],)
            models.execute_kw(db, uid, password, 'saas_server.repository', 'update', [ids])
        return True

    @api.multi
    def restart_server(self):
        for record in self:
            db, uid, password, models = record._get_xmlrpc_object(record.name)
            models.execute_kw(db, uid, password, 'saas_server.client', 'restart_server', [])
        return True

    @api.multi
    def update_templates(self):
        for record in self:
            plans = self.env['saas_portal.plan'].search([('server_id', '=', record.id),
                                                         ('demo_plan_module_ids', '!=', False),
                                                         ('template_id.state', '=', 'template')])
            for plan in plans:
                db, uid, password, models = plan.template_id._get_xmlrpc_object()
                id = models.execute_kw(db, uid, password, 'ir.module.module', 'search',
                                        [[['name', 'in', ['base']]]])
                models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_upgrade', [id])
        return True


    @api.model
    def update_all_templates(self):
        servers = self.env['saas_portal.server'].search([])
        for server in servers:
            server.update_templates()


class SaaSPortalDemoPlanModule(models.Model):
    _name = 'saas_portal.demo_plan_module'
    _rec_name = 'technical_name'

    technical_name = fields.Char('Technical Name')
    url = fields.Char('url', compute="_compute_url", store=True)
    demo_plan_id = fields.Many2one('saas_portal.plan', string='Demo plan where the module intended to be installed', ondelete='cascade', require=True)
    shortdesc = fields.Char('Module Name', translate=True)
    author = fields.Char("Author")
    icon_attachment_id = fields.Many2one('ir.attachment', ondelete='restrict')
    icon = fields.Binary()
    summary = fields.Char('Summary')
    price = fields.Float(string='Price')
    currency = fields.Char("Currency")

    @api.multi
    @api.depends('technical_name')
    def _compute_url(self):
        for record in self:
            record.url = "https://www.odoo.com/apps/modules/%s.0/%s/" % (record.demo_plan_id.server_id.odoo_version, record.technical_name)


class SaaSPortalHiddenDemoPlanModule(models.Model):
    _name = 'saas_portal.hidden_demo_plan_module'
    _rec_name = 'technical_name'

    technical_name = fields.Char('Technical Name')
    demo_plan_id = fields.Many2one('saas_portal.plan', string='Demo plan where the module intended to be installed', ondelete='cascade')


class SaasPortalDemoPlan(models.Model):
    _inherit = 'saas_portal.plan'

    demo_plan_module_ids = fields.One2many('saas_portal.demo_plan_module', 'demo_plan_id',
                                           help="The modules that should be in this demo plan", string='Modules')
    demo_plan_hidden_module_ids = fields.One2many('saas_portal.hidden_demo_plan_module', 'demo_plan_id',
                                           help="The modules that should be in this demo plan", string='Modules')


class SaasPortalDatabase(models.Model):
    _inherit = 'saas_portal.database'

    @api.multi
    def _get_xmlrpc_object(self):
        self.ensure_one()
        url = self.server_id.local_request_scheme + '://' + self.server_id.local_host
        if self.server_id.local_port:
            url += ':' + self.server_id.local_port
        db = self.name
        username = 'admin'
        password = self.password
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        return db, uid, password, xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
