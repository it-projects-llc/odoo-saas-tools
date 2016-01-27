# -*- coding: utf-8 -*-
from openerp import models, fields, api


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
                                                         ('period', '!=', False),
                                                         ('saas_portal_client_id', '=', False)])
        return lines

    @api.multi
    def apply_invoice_lines(self):
        client_obj = self.env['saas_portal.client'].browse(self._context.get('active_id'))
        self.invoice_lines.write({'saas_portal_client_id': client_obj.id})
