from odoo import api, fields, models


class SaasSubscriptionWizard(models.TransientModel):
    _inherit = 'saas_portal.subscription_wizard'

    invoice_line_ids = fields.Many2many(
        'account.invoice.line', string='Add invoice lines to subscription')
    invoice_lines_count = fields.Integer(
        'Invoice lines count', compute='_count_invoice_lines')

    @api.multi
    @api.depends('invoice_line_ids')
    def _count_invoice_lines(self):
        for invoice in self:
            invoice.invoice_lines_count = len(invoice.invoice_line_ids)

    @api.model
    def _get_invoice_lines_wo_client(self, partner_id, plan_id):
        invoice_lines = self.env['account.invoice.line'].search([
            ('partner_id', '=', partner_id),
            ('saas_plan_id', '=', plan_id),
            ('saas_subscription_period', '!=', False),
            ('saas_client_id', '=', False)])
        return invoice_lines

    @api.multi
    def apply_changes(self):
        super(SaasSubscriptionWizard, self).apply_changes()
        self.invoice_line_ids.write({
            'saas_client_id': self.client_id.id,
        })

    @api.model
    def default_get(self, fields):
        result = super(SaasSubscriptionWizard, self).default_get(fields)
        client_id = self.env.context.get('active_id')
        client = self.env['saas_portal.client'].browse(client_id)
        invoice_lines = self._get_invoice_lines_wo_client(
            client.partner_id.id, client.plan_id.id)
        result['invoice_line_ids'] = [(6, 0, invoice_lines.ids)]
        return result
