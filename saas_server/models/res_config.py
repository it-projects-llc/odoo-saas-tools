from openerp import models, fields, api


class SaasServerWizard(models.TransientModel):
    _name = 'saas_server.config.settings'
    _inherit = 'res.config.settings'

    max_backup_open = fields.Integer(
        'Maximum Backup for Active Clients',
        description='Maximum backups to store for active clients'
    )
    max_backup_not_open = fields.Integer(
        'Maximum Backup for Non-Active Clients',
        description='Maximum backups to store for non-active clients'
    )


    @api.model
    def get_default_max_backup(self, fields):
        config_parameter = self.env["ir.config_parameter"]
        return {
            'max_backup_open': int(config_parameter.get_param('saas_server.max_backup_open', default=10)),
            'max_backup_not_open': int(config_parameter.get_param('saas_server.max_backup_not_open', default=3)),
        }

    @api.one
    def set_max_backup(self):
        config_parameter = self.env["ir.config_parameter"]
        config_parameter.set_param('saas_server.max_backup_open', self.max_backup_open)
        config_parameter.set_param('saas_server.max_backup_not_open', self.max_backup_not_open)
