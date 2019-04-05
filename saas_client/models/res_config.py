from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    current_domain = fields.Char(readonly=True)
    domain_change_link = fields.Html(readonly=True)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        current_domain = self.env["ir.config_parameter"].sudo().get_param('web.base.url', default=None)
        link = self.env["ir.config_parameter"].sudo().get_param('saas_client.saas_dashboard', default=None)
        html = link and '<a href="' + link + '" target="_blank" class="oe_link"><i class="fa fa-fw fa-arrow-right"/>' + 'You can change your domain name here' + '</a>' or False
        res.update(
            current_domain=current_domain or False,
            domain_change_link=html,
        )
        return res
