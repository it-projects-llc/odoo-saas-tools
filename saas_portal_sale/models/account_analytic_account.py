# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = ['account.analytic.account',]


    @api.multi
    def _create_invoice(self):
        invoice = super(AccountAnalyticAccount, self)._create_invoice()
        invoice.action_invoice_open()
        if invoice.contract_id:
            client = self.env['saas_portal.client'].search([('contract_id', '=', invoice.contract_id.id)], limit=1)
            client.expiration_datetime = invoice.create_date

        return invoice


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.multi
    def post(self):
        super(AccountPayment, self).post()
        for invoice in self.mapped('invoice_ids').filtered(lambda inv: inv.contract_id):
            client = self.env['saas_portal.client'].search([('contract_id', '=', invoice.contract_id.id)], limit=1)
            client.expiration_datetime = invoice.contract_id.recurring_next_date
