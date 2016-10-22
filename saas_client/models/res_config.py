from odoo import models, fields, api


class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    base_saas_domain = fields.Char('Base SaaS domain')

    current_domain = fields.Char(readonly=True)
    domain_change_link = fields.Html(readonly=True)

    # current_domain
    def get_default_current_domain(self, cr, uid, ids, context=None):
        current_domain = self.pool.get("ir.config_parameter").get_param(cr, uid, 'web.base.url', default=None, context=context)
        return {'current_domain': current_domain or False}

    # domain_change_link
    def get_default_domain_change_link(self, cr, uid, ids, context=None):
        link = self.pool.get("ir.config_parameter").get_param(cr, uid, 'saas_client.saas_dashboard', default=None, context=context)
        html = link and '<a href=' + link + '>' + 'You can change your domain name here' + '</a>' or False
        return {'domain_change_link': html}
