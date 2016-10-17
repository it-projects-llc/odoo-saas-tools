# -*- coding: utf-8 -*-
import requests
from openerp import models, fields, api
import xmlrpclib
import openerp.addons.decimal_precision as dp


class SaasPortalServer(models.Model):
    _inherit = 'saas_portal.server'

    @api.multi
    def _get_xmlrpc_object(self):
        self.ensure_one()

        url = self.local_request_scheme + '://' + self.name
        db = self.name
        username = 'admin'
        password = 'admin'
        # TODO: store username and password in saas_portal.server model
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})

        return db, uid, password, xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

    def _prepare_module(self, module, plan):
        server_domain = self.name.split('.', 1)[1]
        attachment_name = 'addon_' + self.odoo_version + '_' + module['name'] + '.' + server_domain
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

        template_obj = self.env['saas_portal.database']
        plan_obj = self.env['saas_portal.plan']
        server_domain = self.name.split('.', 1)[1]
        template_name = 'template_' + self.odoo_version + '_' + demo_module['name'] + '.' + server_domain
        plan_name = 'Demo ' + self.odoo_version + ' ' + demo_module['display_name']

        if template_obj.search_count([('name', '=', template_name)]) == 0:
            template = template_obj.create({'name': template_name, 'server_id': self.id})
            if plan_obj.search_count([('name', '=', plan_name)]) == 0:
                plan = plan_obj.create({'name': plan_name, 'server_id': self.id, 'template_id': template.id})
                return plan
        else:
            return None

    @api.multi
    def _create_demo_product(self, demo_module, plan):
        self.ensure_one()

        product_template_obj = self.env['product.template']
        product_product_obj = self.env['product.product']
        product_attribute_line_obj = self.env['product.attribute.line']

        product_template_name = demo_module['demo_title']
        product_template = product_template_obj.search([('module_name', '=', demo_module['name'])], limit=1)

        if not product_template:
            product_template = product_template_obj.create({'name': product_template_name,
                                                            'module_name': demo_module['name'],
                                                            'seo_url': demo_module.get('demo_url'),
                                                            'description': demo_module.get('demo_summary'),
                                                            'image': demo_module.get('demo_image'),
                                                            'type': 'service'})
            product_attribute_line = product_attribute_line_obj.create({'product_tmpl_id': product_template.id,
                                                                        'attribute_id': self.env.ref('saas_portal_demo.odoo_version_product_attribute').id,
                                                                        'value_ids': [(6, 0, [self.env.ref('saas_portal_demo.product_attribute_value_8').id,
                                                                                              self.env.ref('saas_portal_demo.product_attribute_value_9').id])],
                                                                    })
        product_product = product_product_obj.create({
            'product_tmpl_id': product_template.id,
            'attribute_value_ids': [(4, self.env.ref('saas_portal_demo.product_attribute_value_%s' % self.odoo_version).id)],
            'variant_plan_id': plan.id,
        })

    @api.multi
    def generate_demo_plans(self):
        demo_plan_module_obj = self.env['saas_portal.demo_plan_module']
        demo_plan_hidden_module_obj = self.env['saas_portal.hidden_demo_plan_module']
        for record in self:
            db, uid, password, models = record._get_xmlrpc_object()
            ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search',
                                    [[['demo_url', '!=', False]]],
                                    )
            modules = models.execute_kw(db, uid, password, 'ir.module.module', 'read', [ids])
            for module in modules:
                plan = record._create_demo_plan(module)

                if not plan:
                    return None

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

        return None

    @api.multi
    def create_demo_templates(self):
        plan_obj = self.env['saas_portal.plan']
        for record in self:
            demo_plan_ids = plan_obj.search([('server_id', '=', record.id), ('template_id.state', '=', 'draft')])
            for plan in demo_plan_ids:
                plan.with_context({'skip_sync_server': True}).create_template()
                addons = plan.demo_plan_module_ids.mapped('technical_name')
                addons.extend(plan.demo_plan_hidden_module_ids.mapped('technical_name'))
                payload = {'install_addons': addons,}
                plan.template_id.upgrade(payload=payload)
                record.action_sync_server()

    @api.multi
    def update_repositories(self):
        for record in self:
            db, uid, password, models = record._get_xmlrpc_object()
            ids = models.execute_kw(db, uid, password, 'saas_server.repository', 'search', [[]],)
            models.execute_kw(db, uid, password, 'saas_server.repository', 'update', [ids])

    @api.multi
    def restart_server(self):
        for record in self:
            db, uid, password, models = record._get_xmlrpc_object()
            models.execute_kw(db, uid, password, 'saas_server.client', 'restart_server', [])


class SaaSPortalDemoPlanModule(models.Model):
    _name = 'saas_portal.demo_plan_module'
    _rec_name = 'technical_name'

    technical_name = fields.Char('Technical Name')
    url = fields.Char('url', compute="_compute_url", store=True)
    demo_plan_id = fields.Many2one('saas_portal.plan', string='Demo plan where the module intended to be installed', ondelete='cascade', require=True)
    shortdesc = fields.Char('Module Name', readonly=True, translate=True)
    author = fields.Char("Author", readonly=True)
    icon_attachment_id = fields.Many2one('ir.attachment', ondelete='restrict')
    icon = fields.Binary()
    summary = fields.Char('Summary', readonly=True)
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
