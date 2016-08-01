# -*- coding: utf-8 -*-
from openerp import models, fields, api
import xmlrpclib
import openerp.addons.decimal_precision as dp


class SaasPortalServer(models.Model):
    _inherit = 'saas_portal.server'

    @api.multi
    def generate_demo_plans(self):
        ir_attachment_obj = self.env['ir.attachment']
        plan_obj = self.env['saas_portal.plan']
        template_obj = self.env['saas_portal.database']
        demo_plan_module_obj = self.env['saas_portal.demo_plan_module']
        demo_plan_hidden_module_obj = self.env['saas_portal.hidden_demo_plan_module']
        product_template_obj = self.env['product.template']
        product_product_obj = self.env['product.product']
        product_attribute_line_obj = self.env['product.attribute.line']
        base_saas_domain = self.env['ir.config_parameter'].get_param('saas_portal.base_saas_domain')
        for record in self:
            url = record.local_request_scheme + '://' + record.name
            db = record.name
            username = 'admin'
            password = 'admin'
            #TODO: store username and password in saas_portal.server model
            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
            ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search',
                                    [[['demo_demonstrative', '=', True]]],
                                    {'limit': 10})
            modules = models.execute_kw(db, uid, password, 'ir.module.module', 'read', [ids])
            for module in modules:
                template_name = 'template_' + record.odoo_version + '_' + module['name'] + '.' + base_saas_domain
                plan_name = 'Demo ' + record.odoo_version + ' ' + module['display_name']
                product_template_name = 'Demo ' + module['display_name']
                if template_obj.search_count([('name', '=', template_name)]) == 0:
                    template = template_obj.create({'name': template_name, 'server_id': record.id})
                    if plan_obj.search_count([('name', '=', plan_name)]) == 0:
                        plan = plan_obj.create({'name': plan_name, 'server_id': record.id, 'template_id': template.id})
                        ir_attachment = ir_attachment_obj.create({'name': template_name, 'type': 'binary', 'db_datas': module['icon_image']})
                        demo_plan_module_obj.create({'technical_name': module['name'],
                                                     'demo_plan_id': plan.id,
                                                     'shortdesc': module['shortdesc'],
                                                     'author': module['author'],
                                                     'icon_attachment_id': ir_attachment.id,
                                                     'summary': module['summary'],
                                                     'price': module['price'],
                                                     'currency': module['currency'],
                                                     })
                        product_template = product_template_obj.search([('module_name', '=', module['name'])], limit=1)
                        if not product_template:
                            product_template = product_template_obj.create({'name': product_template_name,
                                                                            'module_name': module['name'],
                                                                            'seo_url': module.get('demo_url'),
                                                                            'type': 'service'})
                            product_attribute_line = product_attribute_line_obj.create({'product_tmpl_id': product_template.id,
                                                                                        'attribute_id': self.env.ref('saas_portal_demo.odoo_version_product_attribute').id,
                                                                                        'value_ids': [(6, 0, [self.env.ref('saas_portal_demo.product_attribute_value_8').id,
                                                                                                              self.env.ref('saas_portal_demo.product_attribute_value_9').id])],
                                                                                    })
                        product_product = product_product_obj.create({
                                                                      'product_tmpl_id': product_template.id,
                                                                      'attribute_value_ids': [(4, self.env.ref('saas_portal_demo.product_attribute_value_%s' % record.odoo_version).id)],
                                                                      'variant_plan_id': plan.id,
                                                                  })
                        if module.get('demo_addons'):
                            ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search',
                                                    [[['name', 'in', module['demo_addons'].split(',')]]],
                                                    {'limit': 10})
                            addon_modules = models.execute_kw(db, uid, password, 'ir.module.module', 'read', [ids])
                            for addon in addon_modules:
                                attachment_name = 'addon_' + record.odoo_version + '_' + addon['name'] + '.' + base_saas_domain
                                ir_attachment = ir_attachment_obj.create({'name': attachment_name, 'type': 'binary', 'db_datas': addon['icon_image']})
                                demo_plan_module_obj.create({'technical_name': addon['name'],
                                                             'demo_plan_id': plan.id,
                                                             'shortdesc': addon['shortdesc'],
                                                             'author': addon['author'],
                                                             'icon_attachment_id': ir_attachment.id,
                                                             'summary': addon['summary'],
                                                             'price': module['price'],
                                                             'currency': module['currency'],
                                                         })
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
            url = record.local_request_scheme + '://' + record.name
            db = record.name
            username = 'admin'
            password = 'admin'
            #TODO: store username and password in saas_portal.server model
            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
            ids = models.execute_kw(db, uid, password, 'saas_server.repository', 'search', [[]],)
            modules = models.execute_kw(db, uid, password, 'saas_server.repository', 'update', [ids])


class SaaSPortalDemoPlanModule(models.Model):
    _name = 'saas_portal.demo_plan_module'
    _rec_name = 'technical_name'

    technical_name = fields.Char('Technical Name')
    url = fields.Char('url', compute="_compute_url", store=True)
    demo_plan_id = fields.Many2one('saas_portal.plan', string='Demo plan where the module intended to be installed', ondelete='cascade', require=True)
    shortdesc = fields.Char('Module Name', readonly=True, translate=True)
    author = fields.Char("Author", readonly=True)
    icon_attachment_id = fields.Many2one('ir.attachment', ondelete='restrict')
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
