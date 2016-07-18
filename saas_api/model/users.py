from openerp import api, fields, models

class user(models.Model):

    _inherit = "res.users"

    fe_id = fields.Integer('FE id', readonly=True)

    def authenticate(self, db, login, password, user_agent_env):
        res = super(user, self).authenticate(db, login, password, user_agent_env)
        return res