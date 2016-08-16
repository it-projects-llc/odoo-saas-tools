# -*- coding: utf-8 -*-
from openerp import fields
from openerp import models


class SaasPortalServer(models.Model):
    _inherit = 'saas_portal.server'

    ip_address = fields.Char('Server IP Address')
