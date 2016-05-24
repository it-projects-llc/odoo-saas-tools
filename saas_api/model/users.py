from openerp import api, fields, models
import openerp

class user(models.Model):

    _inherit = "res.users"

    fe_id = fields.Integer('FE id', readonly=True)

    # def authenticate(self, db, login, password, user_agent_env):
    #     authenKeySystem = self.pool['ir.config_parameter'].get_param(self.pool.cursor(), openerp.SUPERUSER_ID, 'saas_portal.authenKey')
    #     authenKeySend = user_agent_env.get('authenKey')
    #
    #     if authenKeySend:
    #         if authenKeySystem != authenKeySend:
    #             return {'status': '403', 'value': 'wrong authenKey'}
    #         else:
    #             res = super(user, self).authenticate(db, login, password, user_agent_env)
    #             return res
    #     else:
    #         res = super(user, self).authenticate(db, login, password, user_agent_env)
    #         return res