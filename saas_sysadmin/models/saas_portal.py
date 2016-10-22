# -*- coding: utf-8 -*-
from odoo import fields
from odoo import models


class SaasPortalServer(models.Model):
    _inherit = 'saas_portal.server'

    ip_address = fields.Char('Server IP Address')
