# -*- coding: utf-8 -*-

import requests

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Website(models.Model):

    _inherit = "website"
    URL = 'https://www.google.com/recaptcha/api/siteverify'
    RESPONSE_ATTR = 'g-recaptcha-response'
    ERROR_MAP = {
        'missing-input-secret': 'The secret parameter is missing.',
        'invalid-input-secret':
            'The secret parameter is invalid or malformed.',
        'missing-input-response': 'The response parameter is missing.',
        'invalid-input-response':
            'The response parameter is invalid or malformed.',
        None: 'There was a problem with the captcha entry.',
    }

    google_recaptcha_site_key = fields.Char('Google reCAPTCHA Site Key')
    google_recaptcha_secret_key = fields.Char('Google reCAPTCHA Secret Key')

    @api.multi
    def recaptcha_siteverify(self, response):
        for record in self:
            secret_key = record.google_recaptcha_secret_key
            data = {
                'secret': secret_key,
                'response': response,
                'remoteip': remote_ip,
            }
            data = simplejson.dumps({'secret': record.google_recaptcha_secret_key, 'response': response})
            req_res = requests.post('https://www.google.com/recaptcha/api/siteverify',
                                    data=data)
            res = requests.post(self.URL, data=data).json()

            for error in res.get('error-codes', []):
                raise ValidationError(
                    self.ERROR_MAP.get(
                        error, self.ERROR_MAP[None]
                    )
                )

            if not res.get('success'):
                raise ValidationError(self.ERROR_MAP[None])

            return True
