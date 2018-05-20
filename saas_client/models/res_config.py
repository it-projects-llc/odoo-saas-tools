from odoo import models, fields, api


class BaseConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    base_saas_domain = fields.Char('Base SaaS domain')

    current_domain = fields.Char(readonly=True)
    domain_change_link = fields.Html(readonly=True)

    @api.model
    def get_values(self):
        res = super(BaseConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        current_domain = ICPSudo.get_param('saas_client.current_domain', default=ICPSudo.get_param('web.base.url'))
        link = self.env["ir.config_parameter"].sudo().get_param('saas_client.saas_dashboard', default=None)
        html = link and '<a href=' + link + '>' + 'You can change your domain name here' + '</a>' or False
        res.update(
            current_domain=current_domain,
            domain_change_link=html,
        )
        return res
