from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        '''
        If a invoice line has a product related to a plan that allows promote a
        client from trial and the line has no related client then search a
        trial client for the customer and the plan and start its subscription
        with this invoice line
        '''
        res = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            for line in invoice.invoice_line_ids:
                # set subscription period in invoice line
                attr_vals = line.product_id.attribute_value_ids.filtered(
                    lambda v: v.attribute_id.saas_code ==
                    'subscription_period')
                if attr_vals and attr_vals[0].saas_code_value:
                    line.saas_subscription_period = int(
                        attr_vals[0].saas_code_value)

                plan = line.product_id.saas_plan_id
                if not (plan and plan.non_trial_instances == 'from_trial'):
                    continue
                if line.saas_client_id:
                    continue
                clients = self.env['saas_portal.client'].search([
                        ('partner_id', '=', self.partner_id.id),
                        ('plan_id', '=', line.product_id.saas_plan_id.id),
                        ('invoice_line_ids', '=', False),
                    ], order='id desc')
                if len(clients) < 1:
                    continue
                if len(clients) > 1:
                    # TODO warn support team
                    pass
                clients[0].start_subscription(line.id)
        return res

    @api.multi
    def action_invoice_paid(self):
        '''
        If the invoice has a product related to a plan and the line has no
        related client then send an email to the customer to create a client
        of the plan
        '''
        res = super(AccountInvoice, self).action_invoice_paid()
        for invoice in self:
            plan_ids = set([])
            for line in invoice.invoice_line_ids:
                if not line.product_id.saas_plan_id:
                    continue
                if line.saas_client_id:
                    continue
                plan_ids.add(line.product_id.saas_plan_id.id)
            if plan_ids:
                template = self.env.ref(
                    'saas_portal_sale.email_template_create_saas')
                saas_domain = self.env['ir.config_parameter'].get_param(
                    'saas_portal.base_saas_domain')
                self.with_context(
                    saas_domain=saas_domain, plans=plan_ids
                    ).message_post_with_template(
                    template.id, compositon_mode='comment')
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    date_invoice = fields.Date(
        'Invoice date', related='invoice_id.date_invoice', readonly=True)
    saas_client_id = fields.Many2one(
        'saas_portal.client', 'SaaS client')
    saas_plan_id = fields.Many2one(
        'saas_portal.plan', 'SaaS plan', related='product_id.saas_plan_id',
        readonly=True)
    saas_subscription_period = fields.Integer(
        'SaaS subscription period', readonly=True)
    state = fields.Selection(
        string='State', related='invoice_id.state', readonly=True)
