# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()

        for line in self.invoice_line:
            client_obj = self.env['saas_portal.client'].search([('partner_id', '=', self.partner_id.id),
                                                                ('plan_id', '=', line.plan_id.id)])
            if len(client_obj) == 1:
                payload = {'params': [{'key': 'saas_client.max_users', 'value': line.max_users, 'hidden': True}]}
                self.env['saas.config'].do_upgrade_database(payload, client_obj.id)
                line.saas_portal_client_id = client_obj.id
                client_obj.subscription_start = client_obj.subscription_start or fields.Datetime.now()
        return res

    @api.multi
    def confirm_paid(self):
        for record in self:
            client_plan_id_list = [client.plan_id.id for client in self.env['saas_portal.client'].search([('partner_id', '=', record.partner_id.id)])]
            invoice_plan_id_list = [line.plan_id.id for line in record.invoice_line]
            plans = set(invoice_plan_id_list) - set(client_plan_id_list)
            if plans:
                template = self.env.ref('saas_portal_sale.email_template_create_saas')
                email_ctx = {
                    'default_model': 'account.invoice',
                    'default_res_id': self.id,
                    'default_use_template': bool(template),
                    'default_template_id': template.id,
                    'default_composition_mode': 'comment',
                    'saas_domain': self.env['ir.config_parameter'].get_param('saas_portal.base_saas_domain'),
                    'plans': plans,
                }
                composer = self.env['mail.compose.message'].with_context(email_ctx).create({})
                composer.send_mail()

            return super(AccountInvoice, self).confirm_paid()


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    saas_portal_client_id = fields.Many2one('saas_portal.client', string='SaaS client', help='reference to the SaaS client if this invoice line is created for a SaaS product')
    plan_id = fields.Many2one('saas_portal.plan', related='product_id.plan_id', readonly=True)
    period = fields.Integer(string='Subscription period', help='subsciption period in days', readonly=True, default=0)
    max_users = fields.Integer(help='maximum number of users allowed', readonly=True, default=0)
    addons = fields.Char(help='list of modules to be installed')
    state = fields.Selection(related='invoice_id.state', readonly=True)
    storage_limit = fields.Integer(help='Storage limit in Mb to be setted')

    @api.model
    def create(self, vals):
        # TODO: how to simplify codes handling
        product_obj = self.env['product.product'].browse(vals.get('product_id'))

        attribute_value_obj = product_obj.attribute_value_ids.filtered(lambda r: r.attribute_id.saas_code == 'SUBSCRIPTION_PERIOD')
        period = attribute_value_obj and int(attribute_value_obj[0].saas_code_value) or 0
        vals.update({'period': period})

        attribute_value_obj = product_obj.attribute_value_ids.filtered(lambda r: r.attribute_id.saas_code == 'MAX_USERS')
        max_users = attribute_value_obj and int(attribute_value_obj[0].saas_code_value) or 0
        vals.update({'max_users': max_users})

        attribute_value_obj = product_obj.attribute_value_ids.filtered(lambda r: r.attribute_id.saas_code == 'INSTALL_MODULES')
        addons = attribute_value_obj and attribute_value_obj[0].saas_code_value or ''
        vals.update({'addons': addons})
        
        attribute_value_obj = product_obj.attribute_value_ids.filtered(lambda r: r.attribute_id.saas_code == 'STORAGE_LIMIT')
        storage_limit = attribute_value_obj and int(attribute_value_obj[0].saas_code_value) or 0
        vals.update({'storage_limit': storage_limit})


        return super(AccountInvoiceLine, self).create(vals)
