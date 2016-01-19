__author__ = 'D.H. Bahr <dhbahr@gmail.com>'

from openerp import models, fields, api


class StartWizard(models.Model):
    _name = "saas_portal.start_wizard"

    dbname = fields.Char(required=True)
    lang = fields.Char()
    tz = fields.Char()
    hosting = fields.Char()

    user_id = fields.Integer()
    plan_id = fields.Integer()

    legal_name = fields.Char()
    legal_company = fields.Char()
    legal_vat = fields.Char()
    legal_phone = fields.Char()
    legal_city = fields.Char()
    legal_zip = fields.Char()
    legal_state_id = fields.Integer()
    legal_country_id = fields.Integer()

    order_id = fields.Integer()

    addons = fields.Char()

    done = fields.Boolean(default=False)

    @api.one
    def set_user_id(self, user_id):
        user_orm = self.env["res.users"]
        user = user_orm.browse(user_id)
        partner = user.partner_id

        vals = {
            "user_id": user_id,
            "legal_name": partner.name,
            "legal_phone": partner.phone,
            "legal_company": partner.company_id.partner_id.name,
            "legal_vat": partner.company_id.partner_id.vat,
            "legal_city": partner.city,
            "legal_zip": partner.zip,
            "legal_state_id": partner.state_id.id,
            "legal_country_id": partner.country_id.id,
        }
        self.write(vals)

    @api.one
    def to_dict(self):
        return {
            "dbname": self.dbname,
            "lang": self.lang,
            "tz": self.tz,
            "hosting": self.hosting,
            "user_id": self.user_id,
            "plan_id": self.plan_id,
            "name": self.legal_name,
            "company": self.legal_company,
            "vat": self.legal_vat,
            "phone": self.legal_phone,
            "city": self.legal_city,
            "state_id": self.legal_state_id,
            "country_id": self.legal_country_id,
            "zip": self.legal_zip,
            "addons": self.addons,
        }


class SaasPortalWizardPlan(models.Model):
    _inherit = 'saas_portal.plan'

    post_install_addons = fields.Selection([
        ('none', 'None'),
        ('apps', 'Applications'),
        ('custom', 'Custom'),
    ], string="Available addons", default='none', required=True)
    custom_addons = fields.Many2many('ir.module.module')
