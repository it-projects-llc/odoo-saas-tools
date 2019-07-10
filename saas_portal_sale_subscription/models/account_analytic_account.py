from odoo import api, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _prepare_invoice_line(self, line, invoice_id):
        '''
        Set client in invoice created from contract
        '''
        res = super(AccountAnalyticAccount, self)._prepare_invoice_line(
            line, invoice_id)
        contract = line.analytic_account_id
        if not contract:
            return res
        clients = self.env['saas_portal.client'].search([
            ('contract_id', '=', contract.id),
        ])
        if not clients:
            return res
        res['saas_client_id'] = clients[0].id
        return res
