# -*- coding: utf-8 -*-

from odoo import fields, models


class WebsiteConfigSettings(models.TransientModel):

    _inherit = 'website.config.settings'

    google_recaptcha_site_key = fields.Char()
    google_recaptcha_secret_key = fields.Char()

    def set_google_recaptcha_site_key(self):
        self.env['ir.config_parameter'].set_param(
            'google_recaptcha_site_key', (self.google_recaptcha_site_key or '').strip(), groups=['base.group_system'])

    def get_default_google_recaptcha_site_key(self, fields):
        google_recaptcha_site_key = self.env['ir.config_parameter'].get_param('google_recaptcha_site_key', default='')
        return dict(google_recaptcha_site_key=google_recaptcha_site_key)

    def set_google_recaptcha_secret_key(self):
        self.env['ir.config_parameter'].set_param(
            'google_recaptcha_secret_key', (self.google_recaptcha_secret_key or '').strip(), groups=['base.group_system'])

    def get_default_google_recaptcha_secret_key(self, fields):
        google_recaptcha_secret_key = self.env['ir.config_parameter'].get_param('google_recaptcha_secret_key', default='')
        return dict(google_recaptcha_secret_key=google_recaptcha_secret_key)
