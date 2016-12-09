# -*- coding: utf-8 -*-
from openerp import models, fields, api


class SaasSubscriptionWizard(models.TransientModel):
    _inherit = 'saas_portal.subscription_wizard'

    invoice_line_ids = fields.Many2many('account.invoice.line')
    lines_count = fields.Integer(compute='_compute_lines_count')

    @api.multi
    @api.depends('invoice_line_ids')
    def _compute_lines_count(self):
        for record in self:
            record.lines_count = len(record.invoice_line_ids)

    @api.model
    def default_get(self, fields):
        result = super(SaasSubscriptionWizard, self).default_get(fields)
        client = self.env['saas_portal.client'].browse(self.env.context.get('active_id'))
        lines = self.find_partner_payments(client.partner_id.id, client.plan_id.id)
        result.update({'invoice_line_ids': [(6, 0, lines.ids)]})
        return result

    @api.multi
    def apply_changes(self):
        super(SaasSubscriptionWizard, self).apply_changes()

        self.invoice_line_ids.write({'saas_portal_client_id': self.client_id.id})


    @api.model
    def find_partner_payments(self, partner_id, plan_id):
        lines = self.env['account.invoice.line'].search([('partner_id', '=', partner_id),
                                                         ('product_id.plan_id', '=', plan_id),
                                                         ('period', '!=', False),
                                                         ('saas_portal_client_id', '=', False)])
        return lines
