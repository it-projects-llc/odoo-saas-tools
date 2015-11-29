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

    saas_portal_client_id = fields.Many2one('saas_portal.client')
    plan_id = fields.Many2one('saas_portal.plan', related='product_id.plan_id', readonly=True)
    period = fields.Integer(string='Subscription period', related="product_id.period", readonly=True)


class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'

    subscription_start = fields.Datetime(string="Subscription start")
    invoice_lines = fields.One2many('account.invoice.line', 'saas_portal_client_id')


class FindPaymentsWizard(models.TransientModel):
    _name = 'saas_portal.find_payments_wizard'

    invoice_lines = fields.Many2many('account.invoice.line')

    @api.model
    def default_get(self, fields):
        res = super(FindPaymentsWizard, self).default_get(fields)
        client_obj = self.env['saas_portal.client'].browse(self._context.get('active_id'))
        lines = self.env['account.invoice.line'].search([('partner_id', '=', client_obj.partner_id.id),
                                                         ('product_id.plan_id', '=', client_obj.plan_id.id),
                                                         ('product_id.period', '!=', False),
                                                         ('saas_portal_client_id', '=', False)])

        res.update({'invoice_lines': [(6, 0, lines.ids)]})
        return res

    @api.multi
    def apply_invoice_lines(self):
        client_obj = self.env['saas_portal.client'].browse(self._context.get('active_id'))
        self.invoice_lines.write({'saas_portal_client_id': client_obj.id})

        if client_obj.subscription_start:
            for line in self.invoice_lines:
                if not client_obj.expiration_datetime:
                    client_obj.expiration_datetime = datetime.strptime(client_obj.subscription_start, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(days=line.product_id.period)
                else:
                    client_obj.expiration_datetime = datetime.strptime(client_obj.expiration_datetime, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(days=line.product_id.period)
