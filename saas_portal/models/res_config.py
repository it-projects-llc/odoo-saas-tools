from openerp import models, fields
from openerp.addons.web.http import request
import urlparse

class SaasPortalConfigWizard(models.TransientModel):
    _name = 'saas_portal.config.settings'
    _inherit = 'res.config.settings'

    base_saas_domain = fields.Char('Base SaaS domain')

    page_for_maximumdb = fields.Char(help='Redirection url for maximum non-trial databases limit exception')
    page_for_maximumtrialdb = fields.Char(help='Redirection url for maximum trial databases limit exception')
    page_for_nonfree_subdomains = fields.Char(help='Redirection url from /page/start when subdomains is not free and not paid')

    expiration_notify_in_advance = fields.Char(help='Notify partners when less then defined number of days left befor expiration')

    module_saas_portal_sale_online = fields.Boolean(string='Sale SaaS from website shop', help='Use saas_portal_sale_online module')

    # base_saas_domain
    def get_default_base_saas_domain(self, cr, uid, ids, context=None):
        base_saas_domain = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_portal.base_saas_domain", default=None, context=context)
        if base_saas_domain is None:
            domain = self.pool.get("ir.config_parameter").get_param(cr, uid, "web.base.url", context=context)
            try:
                base_saas_domain = urlparse.urlsplit(domain).netloc.split(':')[0]
            except Exception:
                pass
        return {'base_saas_domain': base_saas_domain or False}

    def set_base_saas_domain(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "saas_portal.base_saas_domain", record.base_saas_domain or '', context=context)

    # page_for_maximumdb
    def get_default_page_for_maximumdb(self, cr, uid, ids, context=None):
        page_for_maximumdb = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_portal.page_for_maximumdb", default='/', context=context)
        return {'page_for_maximumdb': page_for_maximumdb or '/'}

    def set_page_for_maxumumdb(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "saas_portal.page_for_maximumdb", record.page_for_maximumdb or '/', context=context)

    # page_for_maximumtrialdb
    def get_default_page_for_maximumtrialdb(self, cr, uid, ids, context=None):
        page_for_maximumtrialdb = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_portal.page_for_maximumtrialdb", default='/', context=context)
        return {'page_for_maximumtrialdb': page_for_maximumtrialdb or '/'}

    def set_page_for_maxumumtrialdb(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "saas_portal.page_for_maximumtrialdb", record.page_for_maximumtrialdb or '/', context=context)

    # page_for_nonfree_subdomains
    def get_default_page_for_nonfree_subdomains(self, cr, uid, ids, context=None):
        page_for_nonfree_subdomains = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_portal.page_for_nonfree_subdomains", default='/', context=context)
        return {'page_for_nonfree_subdomains': page_for_nonfree_subdomains or '/'}

    def set_page_for_nonfree_subdomains(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "saas_portal.page_for_nonfree_subdomains", record.page_for_nonfree_subdomains or '/', context=context)

    # expiration_notify_in_advance
    def get_default_expiration_notify_in_advance(self, cr, uid, ids, context=None):
        expiration_notify_in_advance = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_portal.expiration_notify_in_advance", default='0', context=context)
        return {'expiration_notify_in_advance': expiration_notify_in_advance or '0'}

    def set_expiration_notify_in_advance(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "saas_portal.expiration_notify_in_advance", record.expiration_notify_in_advance or '0', context=context)

