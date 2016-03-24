from openerp import models, fields


class SaasServerWizard(models.TransientModel):
    _name = 'saas_server.config.settings'
    _inherit = 'res.config.settings'
