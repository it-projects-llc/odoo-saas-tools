# -*- coding: utf-8 -*-

import requests
import simplejson

from odoo import api, fields, models


class Website(models.Model):

    _inherit = "website"

    google_recaptcha_site_key = fields.Char('Google reCAPTCHA Site Key')
    google_recaptcha_secret_key = fields.Char('Google reCAPTCHA Secret Key')

    @api.multi
    def recaptcha_siteverify(self, response):
        for record in self:
            req_res = requests.post('https://www.google.com/recaptcha/api/siteverify',
                                    data={'secret': record.google_recaptcha_secret_key,
                                          'response': response})
            res = simplejson.loads(req_res.content)
            print '\n\n\n', 'reCAPTCHA res', res, '\n\n\n'
            return res.get('success')
