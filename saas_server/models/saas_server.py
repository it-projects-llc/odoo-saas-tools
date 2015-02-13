import os
import openerp
from openerp import SUPERUSER_ID
from openerp import models, fields


def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


class SaasServerClient(models.Model):
    _name = 'saas_server.client'

    name = fields.Char('Database name', readonly=True)
    client_id = fields.Char('Client ID', readonly=True, select=True)
    users_len = fields.Integer('Count users')
    file_storage = fields.Integer('File storage (MB)')
    db_storage = fields.Integer('DB storage (MB)')

    def update_all(self, cr, uid, server_db):
        db_list = openerp.service.db.exp_list()
        try:
            client_list.remove(server_db)
        except:
            pass

        res = []
        for db in db_list:
            registry = openerp.modules.registry.RegistryManager.get(db)
            with registry.cursor() as db_cr:
                client_id = registry['ir.config_parameter'].get_param(db_cr,
                                                SUPERUSER_ID, 'database.uuid')
                users = registry['res.users'].search(db_cr, SUPERUSER_ID,
                                                     [('share', '=', False)])
                users_len = len(users)
                data_dir = openerp.tools.config['data_dir']

                file_storage = get_size('%s/filestore/%s' % (data_dir, db))
                file_storage = int(file_storage / (1024 * 1024))

                db_cr.execute("select pg_database_size('%s')" % db)
                db_storage = db_cr.fetchone()[0]
                db_storage = int(db_storage / (1024 * 1024))

                data = {
                    'name': db,
                    'client_id': client_id,
                    'users_len': users_len,
                    'file_storage': file_storage,
                    'db_storage': db_storage,
                }
                oid = self.search(cr, uid, [('client_id', '=', client_id)])
                if not oid:
                    self.create(cr, uid, data)
                else:
                    self.write(cr, uid, oid, data)
                res.append(data)

        return res
