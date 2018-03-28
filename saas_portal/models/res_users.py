from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    support_team_id = fields.Many2one('saas_portal.support_team',
                                      'Support Team',
                                      help='Support team for SaaS')

    def __init__(self, pool, cr):
        super(ResUsers, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        self.SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        self.SELF_WRITEABLE_FIELDS.extend(['support_team_id'])

    @api.model
    def create(self, values):
        # overridden to signup along with creation of db through saas backend wizard
        user = super(ResUsers, self).create(values)
        if self.env.context.get('saas_signup'):
            user.partner_id.signup_prepare()
        return user
