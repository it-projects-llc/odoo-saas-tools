__author__ = 'D.H. Bahr <dhbahr@gmail.com>'

from openerp import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"

    terms_n_conds = fields.Html(string="Terms & Conditions")
