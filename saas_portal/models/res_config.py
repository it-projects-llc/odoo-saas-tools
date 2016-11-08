# -*- coding: utf-8 -*-
from odoo import models, fields, api
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
    @api.model
    def get_default_base_saas_domain(self, fields):
        base_saas_domain = self.env["ir.config_parameter"].get_param("saas_portal.base_saas_domain", default=None)
        if base_saas_domain is None:
            domain = self.env["ir.config_parameter"].get_param("web.base.url")
            try:
                base_saas_domain = urlparse.urlsplit(domain).netloc.split(':')[0]
            except Exception:
                pass
        return {'base_saas_domain': base_saas_domain or False}

    @api.multi
    def set_base_saas_domain(self):
        config_parameters = self.env["ir.config_parameter"]
        for record in self:
            config_parameters.set_param("saas_portal.base_saas_domain", record.base_saas_domain or '')

    # page_for_maximumdb
    @api.model
    def get_default_page_for_maximumdb(self, fields):
        page_for_maximumdb = self.env["ir.config_parameter"].get_param("saas_portal.page_for_maximumdb", default='/')
        return {'page_for_maximumdb': page_for_maximumdb or '/'}

    @api.multi
    def set_page_for_maxumumdb(self):
        config_parameters = self.env["ir.config_parameter"]
        for record in self:
            config_parameters.set_param("saas_portal.page_for_maximumdb", record.page_for_maximumdb or '/')

    # page_for_maximumtrialdb
    @api.model
    def get_default_page_for_maximumtrialdb(self, fields):
        page_for_maximumtrialdb = self.env["ir.config_parameter"].get_param("saas_portal.page_for_maximumtrialdb", default='/')
        return {'page_for_maximumtrialdb': page_for_maximumtrialdb or '/'}

    @api.multi
    def set_page_for_maxumumtrialdb(self):
        config_parameters = self.env["ir.config_parameter"]
        for record in self:
            config_parameters.set_param("saas_portal.page_for_maximumtrialdb", record.page_for_maximumtrialdb or '/')

    # page_for_nonfree_subdomains
    @api.model
    def get_default_page_for_nonfree_subdomains(self, fields):
        page_for_nonfree_subdomains = self.env["ir.config_parameter"].get_param("saas_portal.page_for_nonfree_subdomains", default='/')
        return {'page_for_nonfree_subdomains': page_for_nonfree_subdomains or '/'}

    @api.multi
    def set_page_for_nonfree_subdomains(self):
        config_parameters = self.env["ir.config_parameter"]
        for record in self:
            config_parameters.set_param("saas_portal.page_for_nonfree_subdomains", record.page_for_nonfree_subdomains or '/')

    # expiration_notify_in_advance
    @api.model
    def get_default_expiration_notify_in_advance(self, fields):
        expiration_notify_in_advance = self.env["ir.config_parameter"].get_param("saas_portal.expiration_notify_in_advance", default='0')
        return {'expiration_notify_in_advance': expiration_notify_in_advance or '0'}

    @api.multi
    def set_expiration_notify_in_advance(self):
        config_parameters = self.env["ir.config_parameter"]
        for record in self:
            config_parameters.set_param("saas_portal.expiration_notify_in_advance", record.expiration_notify_in_advance or '0')
