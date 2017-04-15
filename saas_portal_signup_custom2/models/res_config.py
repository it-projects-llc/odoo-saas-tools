# -*- coding: utf-8 -*-

from odoo import fields, models


class WebsiteConfigSettings(models.TransientModel):

    _inherit = 'website.config.settings'

    google_recaptcha_site_key = fields.Char('Google reCAPTCHA Site Key', related='website_id.google_recaptcha_site_key')
    google_recaptcha_secret_key = fields.Char('Google reCAPTCHA Secret Key', related='website_id.google_recaptcha_secret_key')
