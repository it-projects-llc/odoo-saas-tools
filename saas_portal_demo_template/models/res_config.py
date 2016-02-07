from openerp import models, fields, api


class SaasPortalConfigWizard(models.TransientModel):
    _inherit = 'saas_portal.config.settings'

    demo_client_name = fields.Char(
        'Demo Client Name',
        required=True
    )
    demo_plan_id = fields.Many2one(
        'saas_portal.plan',
        'Demo Plan',
        required=True,
    )
    @api.multi
    def get_default_demo_details(self):
        company = self.env.user.company_id
        return {'demo_client_name': company.demo_client_name,
                'demo_plan_id': company.demo_plan_id.id,
                }

    @api.multi
    def set_demo_details(self):
        company = self.env.user.company_id
        company.demo_client_name = self.demo_client_name
        company.demo_plan_id = self.demo_plan_id.id
