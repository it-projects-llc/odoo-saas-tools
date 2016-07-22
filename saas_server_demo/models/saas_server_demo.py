# -*- coding: utf-8 -*-
import os
import openerp
from openerp import models, fields, api
from openerp.exceptions import ValidationError


class SaasServerRepository(models.Model):
    _name = 'saas_server.repository'

    path = fields.Selection('_get_repositories', string='Repository', required='True')

    _sql_constraints = [('path_unique', 'unique(path)', 'Repository already exists.')]

    @api.model
    def _get_repositories(self):
        root_path = os.path.abspath(os.path.expanduser(os.path.expandvars(os.path.dirname(openerp.__file__))))
        base_addons = os.path.join(root_path, 'addons')
        main_addons = os.path.abspath(os.path.join(root_path, '../addons'))
        paths = [(p, os.path.basename(p)) for p in openerp.conf.addons_paths if p not in [base_addons, main_addons] \
                 and os.path.exists(p + '/.git')]
        return paths

