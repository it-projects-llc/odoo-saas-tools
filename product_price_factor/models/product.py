# -*- coding: utf-8 -*-
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    @api.multi
    def _get_price_factor(self):
        active_id = self.env.context.get('active_id')
        if not active_id:
            return

        for obj in self:
            for price_id in obj.price_ids:
                if price_id.product_tmpl_id.id == active_id:
                    obj.price_factor = price_id.price_factor

    def _set_price_factor(self):
        value = self.price_factor
        id = self.id
        active_id = self.env.context.get('active_id')
        if not active_id:
            return

        p_obj = self.env['product.attribute.price']
        p_ids = p_obj.search([('value_id', '=', id), ('product_tmpl_id', '=', active_id)])
        if p_ids:
            p_ids.write({'price_factor': value})
        else:
            p_obj.create({
                'product_tmpl_id': active_id,
                'value_id': id,
                'price_factor': value,
            })

    price_factor = fields.Float(compute="_get_price_factor", string='Attribute Price Factor',
                                        inverse=_set_price_factor,
                                        digits=dp.get_precision('Product Price'))


class ProductAttributePrice(models.Model):
    _inherit = "product.attribute.price"

    price_factor = fields.Float('Price Factor', digits=dp.get_precision('Product Price'), default=1.0)


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def price_compute(self, price_type, uom=False, currency=False, company=False):
        # TDE FIXME: delegate to template or not ? fields are reencoded here ...
        # compatibility about context keys used a bit everywhere in the code
        if not uom and self._context.get('uom'):
            uom = self.env['product.uom'].browse(self._context['uom'])
        if not currency and self._context.get('currency'):
            currency = self.env['res.currency'].browse(self._context['currency'])

        products = self
        if price_type == 'standard_price':
            # standard_price field can only be seen by users in base.group_user
            # Thus, in order to compute the sale price from the cost for users not in this group
            # We fetch the standard price as the superuser
            products = self.with_context(force_company=company and company.id or self._context.get('force_company', self.env.user.company_id.id)).sudo()

        prices = dict.fromkeys(self.ids, 0.0)
        for product in products:
            prices[product.id] = product[price_type] or 0.0
            if price_type == 'list_price':
                for line in product.product_tmpl_id.attribute_line_ids:
                    for value in product.attribute_value_ids.filtered(lambda r: r.attribute_id == line.attribute_id):
                        for price in value.price_ids.filtered(lambda r: r.product_tmpl_id == product.product_tmpl_id):
                            prices[product.id] = (prices[product.id] + price.price_extra) * price.price_factor

            if uom:
                prices[product.id] = product.uom_id._compute_price(prices[product.id], uom)

            # Convert from current user company currency to asked one
            # This is right cause a field cannot be in more than one currency
            if currency:
                prices[product.id] = product.currency_id.compute(prices[product.id], currency)

        return prices


class ProductAttributeLine(models.Model):
    _inherit = "product.attribute.line"
    _order = 'sequence'

    def _default_sequence(self):
        # without this function there was a bug when attributes were created
        # from Product Variants tab. If several attributes were created without pushing the save button
        # sequence got the same value for their attribute lines. And if there was no lines before
        # sequence got False for the first attribute
        num = self.search_count([]) + 1
        return num

    sequence = fields.Integer('Sequence', help="Determine the display order", required=True, default=_default_sequence)
