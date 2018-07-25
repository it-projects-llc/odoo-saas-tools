# Copyright 2018 Ildar Nasyrov <https://it-projects.info/team/iledarn>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_saas_server_backup_ftp = fields.Boolean(string='Use SFTP Backup profile', help='Use saas_server_backup_ftp module')
