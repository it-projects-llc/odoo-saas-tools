from odoo import models, fields, api


class SaasPortalConfigWizard(models.TransientModel):
    _inherit = 'res.config.settings'

    base_saas_domain = fields.Char('Base SaaS domain')

    page_for_maximumdb = fields.Char(help='Redirection url for maximum non-trial databases limit exception')
    page_for_maximumtrialdb = fields.Char(help='Redirection url for maximum trial databases limit exception')
    page_for_nonfree_subdomains = fields.Char(help='Redirection url from /page/start when subdomains is not free and not paid')

    expiration_notify_in_advance = fields.Char(help='Notify partners when less then defined number of days left befor expiration')

    module_saas_portal_sale_online = fields.Boolean(string='Sale SaaS from website shop', help='Use saas_portal_sale_online module')
    module_saas_server_backup_rotate = fields.Boolean(string='Rotate backups', help='Use saas_server_backup_rotate module')

    @api.multi
    def set_values(self):
        super(SaasPortalConfigWizard, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("saas_portal.base_saas_domain", self.base_saas_domain)
        ICPSudo.set_param("saas_portal.page_for_maximumdb", self.page_for_maximumdb)
        ICPSudo.set_param("saas_portal.page_for_maximumtrialdb", self.page_for_maximumtrialdb)
        ICPSudo.set_param("saas_portal.page_for_nonfree_subdomains", self.page_for_nonfree_subdomains)
        ICPSudo.set_param("saas_portal.expiration_notify_in_advance", self.expiration_notify_in_advance)

    @api.model
    def get_values(self):
        res = super(SaasPortalConfigWizard, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            base_saas_domain=ICPSudo.get_param('saas_portal.base_saas_domain'),
            page_for_maximumdb=ICPSudo.get_param('saas_portal.page_for_maximumdb'),
            page_for_maximumtrialdb=ICPSudo.get_param('saas_portal.page_for_maximumtrialdb'),
            page_for_nonfree_subdomains=ICPSudo.get_param('saas_portal.page_for_nonfree_subdomains'),
            expiration_notify_in_advance=ICPSudo.get_param('saas_portal.expiration_notify_in_advance'),
        )
        return res
