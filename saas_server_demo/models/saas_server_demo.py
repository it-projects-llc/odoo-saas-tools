# -*- coding: utf-8 -*-
import os
import logging
import odoo
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
import subprocess
import tempfile

_logger = logging.getLogger(__name__)

class SaasServerRepository(models.Model):
    _name = 'saas_server.repository'

    path = fields.Selection('_get_repositories', string='Repository', required='True')

    _sql_constraints = [('path_unique', 'unique(path)', 'Repository already exists.')]

    @api.model
    def _get_repositories(self):
        root_path = os.path.abspath(os.path.expanduser(os.path.expandvars(os.path.dirname(odoo.__file__))))
        base_addons = os.path.join(root_path, 'addons')
        main_addons = os.path.abspath(os.path.join(root_path, '../addons'))
        paths = [(p, os.path.basename(p))
                 for p in odoo.conf.addons_paths
                 if p not in [base_addons, main_addons] and os.path.exists(p + '/.git')]
        return paths

    @api.multi
    def update(self):
        cwd = os.getcwd()
        ret = []
        for record in self:
            stderr_fd, stderr_path = tempfile.mkstemp(text=True)
            os.chdir(record.path)
            try:
                status = subprocess.call(['git', 'pull', '--ff-only'], stderr=stderr_fd)
                os.close(stderr_fd)  # ensure flush before reading
                stderr_fd = None  # avoid closing again in finally block
                fobj = open(stderr_path, 'r')
                error_message = fobj.read()
                fobj.close()
                if not error_message:
                    error_message = 'No diagnosis message was provided'
                else:
                    error_message = 'The following diagnosis message was provided:\n' + error_message
                if status:
                    _logger.exception("The command 'git pull' failed with error code = %s. Message: %s" % (status, error_message))

                ret.append({'record.path': status})
            finally:
                if stderr_fd is not None:
                    os.close(stderr_fd)

        os.chdir(cwd)
        self.env['ir.module.module'].update_list()
        return ret
