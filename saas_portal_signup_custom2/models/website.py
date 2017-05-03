# -*- coding: utf-8 -*-

import requests

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Website(models.Model):

    _inherit = "website"
    URL = 'https://www.google.com/recaptcha/api/siteverify'

    google_recaptcha_site_key = fields.Char('Google reCAPTCHA Site Key')
    google_recaptcha_secret_key = fields.Char('Google reCAPTCHA Secret Key')

    @api.multi
    def recaptcha_siteverify(self, response):
        for record in self:
            secret_key = record.google_recaptcha_secret_key
            data = {
                'secret': secret_key,
                'response': response,
            }
            res = requests.post(self.URL, data=data).json()
            if res.get('success'):
                return True
            return False
