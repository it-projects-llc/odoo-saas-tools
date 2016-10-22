# -*- coding: utf-8 -*-
from odoo import models


class SaasServerWizard(models.TransientModel):
    _name = 'saas_server.config.settings'
    _inherit = 'res.config.settings'
