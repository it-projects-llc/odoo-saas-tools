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
                                        digits_compute=dp.get_precision('Product Price'))


class ProductAttributePrice(models.Model):
    _inherit = "product.attribute.price"

    price_factor = fields.Float('Price Factor', digits_compute=dp.get_precision('Product Price'), default=1.0)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _price_get(self, products, ptype='list_price'):
        context = self.env.context
        if 'currency_id' in context:
            pricetype_obj = self.env['product.price.type']
            price_type_id = pricetype_obj.search([('field', '=', ptype)])[0]
            price_type_currency_id = pricetype_obj.browse(price_type_id).currency_id.id

        res = {}
        for product in products:
            # standard_price field can only be seen by users in base.group_user
            # Thus, in order to compute the sale price from the cost price for users not in this group
            # We fetch the standard price as the superuser
            if ptype != 'standard_price':
                res[product.id] = product[ptype] or 0.0
            else:
                company_id = product.env.user.company_id.id
                product = product.with_context(force_company=company_id)
                res[product.id] = res[product.id] = product.sudo()[ptype]
            if ptype == 'list_price':
                if product._name == "product.product":
                    for attribute_line_obj in product.product_tmpl_id.attribute_line_ids:
                        for value_obj in product.attribute_value_ids:
                            if value_obj.attribute_id.id == attribute_line_obj.attribute_id.id:
                                for price_id in value_obj.price_ids:
                                    if price_id.product_tmpl_id.id == product.product_tmpl_id.id:
                                        res[product.id] = (res[product.id] + price_id.price_extra) * price_id.price_factor

            if 'uom' in context:
                uom = product.uom_id or product.uos_id
                res[product.id] = uom._compute_price(res[product.id], context['uom'])
            # Convert from price_type currency to asked one
            if 'currency_id' in context:
                # Take the price_type currency from the product field
                # This is right cause a field cannot be in more than one currency
                res[product.id] = self.env['res.currency'].compute(price_type_currency_id,
                                                                        context['currency_id'], res[product.id])

        return res


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
