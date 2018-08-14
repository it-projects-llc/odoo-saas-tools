from odoo import models, fields


class ProductAttributeSaaS(models.Model):
    _inherit = 'product.attribute'

    def _get_saas_codes(self):
        res = super(ProductAttributeSaaS, self)._get_saas_codes()
        res.extend([
            ('install_modules', 'install_modules'),
            ('subscription_period', 'subscription_period'),
        ])
        return res


class ProductAttributeValueSaaS(models.Model):
    _inherit = 'product.attribute.value'

    saas_code_value = fields.Char('SaaS code value')
