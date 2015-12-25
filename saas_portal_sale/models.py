# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ProductTemplateSaaS(models.Model):
    _inherit = 'product.template'

    plan_id = fields.Many2one('saas_portal.plan', string='Plan')
    period = fields.Integer(string='Subscription period')


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    saas_portal_client_id = fields.Many2one('saas_portal.client', string='SaaS client', help='reference to the SaaS client if this invoice line is created for a SaaS product')
    plan_id = fields.Many2one('saas_portal.plan', related='product_id.plan_id', readonly=True)
    period = fields.Integer(string='Subscription period', help='subsciption period in days', related="product_id.period", readonly=True)
    state = fields.Selection(related='invoice_id.state', readonly=True)


class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'

    subscription_start = fields.Datetime(string="Subscription start", track_visibility='onchange')
    expiration_datetime = fields.Datetime(string="Expiration", compute='_handle_paid_invoices',
                                          store=True,
                                          help='Subscription start plus all paid days from related invoices')
    invoice_lines = fields.One2many('account.invoice.line', 'saas_portal_client_id')
    trial = fields.Boolean('Trial', help='indication of trial clients', default=False, store=True, readonly=True, compute='_handle_paid_invoices')

    @api.multi
    @api.depends('invoice_lines.invoice_id.state')
    def _handle_paid_invoices(self):
        for client_obj in self:
            client_obj.expiration_datetime = datetime.strptime(client_obj.create_date, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(hours=client_obj.plan_id.expiration)  # for trial
            days = 0
            for line in self.env['account.invoice.line'].search([('saas_portal_client_id', '=', client_obj.id), ('invoice_id.state', '=', 'paid')]):
                days += line.product_id.period
            if days != 0:
                client_obj.expiration_datetime = datetime.strptime(client_obj.subscription_start or client_obj.create_date, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(days=days)
            client_obj.trial = not bool(days)


class FindPaymentsWizard(models.TransientModel):
    _name = 'saas_portal.find_payments_wizard'

    invoice_lines = fields.Many2many('account.invoice.line')

    @api.model
    def default_get(self, fields):
        res = super(FindPaymentsWizard, self).default_get(fields)
        client_obj = self.env['saas_portal.client'].browse(self._context.get('active_id'))
        lines = self.find_partner_payments(client_obj.partner_id.id, client_obj.plan_id.id)
        res.update({'invoice_lines': [(6, 0, lines.ids)]})
        return res

    @api.model
    def find_partner_payments(self, partner_id, plan_id):
        lines = self.env['account.invoice.line'].search([('partner_id', '=', partner_id),
                                                         ('product_id.plan_id', '=', plan_id),
                                                         ('product_id.period', '!=', False),
                                                         ('saas_portal_client_id', '=', False)])
        return lines

    @api.multi
    def apply_invoice_lines(self):
        client_obj = self.env['saas_portal.client'].browse(self._context.get('active_id'))
        self.invoice_lines.write({'saas_portal_client_id': client_obj.id})


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()

        for line in self.invoice_line_ids:
            client_obj = self.env['saas_portal.client'].search([('partner_id', '=', self.partner_id.id),
                                                                ('plan_id', '=', line.plan_id.id)])
            if len(client_obj) == 1:
                line.saas_portal_client_id = client_obj.id
                client_obj.subscription_start = client_obj.subscription_start or fields.Datetime.now()
        return res

    @api.multi
    def confirm_paid(self):
        client_plan_id_list = self.env['saas_portal.client'].search([('partner_id', '=', self.partner_id.id)]).mapped(lambda r: r.plan_id.id)
        invoice_plan_id_list = [line.plan_id.id for line in self.invoice_line_ids]
        plans = [plan for plan in invoice_plan_id_list if plan not in client_plan_id_list]

        if plans:
            template = self.env.ref('saas_portal_sale.email_template_create_saas')
            self.with_context(saas_domain=self.env['ir.config_parameter'].get_param('saas_portal.base_saas_domain'),
                              plans=plans).message_post_with_template(template.id, composition_mode='comment')
        return super(AccountInvoice, self).confirm_paid()


class SaasPortalPlan(models.Model):
    _inherit = 'saas_portal.plan'

    @api.multi
    def create_new_database(self, dbname=None, client_id=None, partner_id=None, user_id=None, notify_user=False, trial=False, support_team_id=None):
        res = super(SaasPortalPlan, self).create_new_database(dbname=dbname,
                                                              client_id=client_id,
                                                              partner_id=partner_id,
                                                              user_id=user_id,
                                                              notify_user=notify_user,
                                                              trial=trial,
                                                              support_team_id=support_team_id)
        lines = self.env['saas_portal.find_payments_wizard'].find_partner_payments(partner_id=partner_id, plan_id=self.id)
        client_obj = self.env['saas_portal.client'].browse(res.get('id'))
        if not trial:
            client_obj.subscription_start = client_obj.create_date
        lines.write({'saas_portal_client_id': client_obj.id})
        return res
