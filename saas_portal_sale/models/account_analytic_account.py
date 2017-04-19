# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = ['account.analytic.account',]


    @api.multi
    def _create_invoice(self):
        invoice = super(AccountAnalyticAccount, self)._create_invoice()
        invoice.action_invoice_open()
        return invoice
