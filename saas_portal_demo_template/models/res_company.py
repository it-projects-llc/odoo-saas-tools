from openerp import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    demo_client_name = fields.Char(
        'Demo Client Name',
        required=True
    )
    demo_plan_id = fields.Many2one(
        'saas_portal.plan',
        'Demo Plan',
        required=True,
    )