from odoo import models, fields, api


class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    base_saas_domain = fields.Char('Base SaaS domain')

    current_domain = fields.Char(readonly=True)
    domain_change_link = fields.Html(readonly=True)

    # current_domain
    @api.model
    def get_default_current_domain(self, fields):
        current_domain = self.env["ir.config_parameter"].get_param('web.base.url', default=None)
        return {'current_domain': current_domain or False}

    # domain_change_link
    @api.model
    def get_default_domain_change_link(self, fields):
        link = self.env["ir.config_parameter"].get_param('saas_client.saas_dashboard', default=None)
        html = link and '<a href=' + link + '>' + 'You can change your domain name here' + '</a>' or False
        return {'domain_change_link': html}
