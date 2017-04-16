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
        print '\n\n\n', 'response', response, '\n\n\n'
        for record in self:
            print '\n\n\n', 'secret key', record.google_recaptcha_secret_key, '\n\n\n'
            data = simplejson.dumps({'secret': record.google_recaptcha_secret_key, 'response': response})
            req_res = requests.post('https://www.google.com/recaptcha/api/siteverify',
                                    data=data)
            res = simplejson.loads(req_res.content)
            print '\n\n\n', 'reCAPTCHA res', res, '\n\n\n'
            return res.get('success')
