# -*- coding: utf-8 -*-
from openerp import models
from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp


class ProductAttributeValue(osv.osv):
    _inherit = "product.attribute.value"

    def _get_price_factor(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, 0)
        if not context.get('active_id'):
            return result

        for obj in self.browse(cr, uid, ids, context=context):
            for price_id in obj.price_ids:
                if price_id.product_tmpl_id.id == context.get('active_id'):
                    result[obj.id] = price_id.price_factor
                    break
        return result

    def _set_price_factor(self, cr, uid, id, name, value, args, context=None):
        if context is None:
            context = {}
        if 'active_id' not in context:
            return None
        p_obj = self.pool['product.attribute.price']
        p_ids = p_obj.search(cr, uid, [('value_id', '=', id), ('product_tmpl_id', '=', context['active_id'])], context=context)
        if p_ids:
            p_obj.write(cr, uid, p_ids, {'price_factor': value}, context=context)
        else:
            p_obj.create(cr, uid, {
                'product_tmpl_id': context['active_id'],
                'value_id': id,
                'price_factor': value,
                }, context=context)

    _columns = {
        'price_factor': fields.function(_get_price_factor, type='float', string='Attribute Price Factor',
                                        fnct_inv=_set_price_factor,
                                        digits_compute=dp.get_precision('Product Price')),
    }


class ProductAttributePrice(osv.osv):
    _inherit = "product.attribute.price"
    _columns = {
        'price_factor': fields.float('Price Factor', digits_compute=dp.get_precision('Product Price')),
    }

    _defaults = {
        'price_factor': 1.0,
    }


class ProductTemplate(osv.osv):
    _inherit = "product.template"

    def _price_get(self, cr, uid, products, ptype='list_price', context=None):
        if context is None:
            context = {}

        if 'currency_id' in context:
            pricetype_obj = self.pool.get('product.price.type')
            price_type_id = pricetype_obj.search(cr, uid, [('field', '=', ptype)])[0]
            price_type_currency_id = pricetype_obj.browse(cr, uid, price_type_id).currency_id.id

        res = {}
        product_uom_obj = self.pool.get('product.uom')
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
                res[product.id] = product_uom_obj._compute_price(cr, uid,
                                                                 uom.id, res[product.id], context['uom'])
            # Convert from price_type currency to asked one
            if 'currency_id' in context:
                # Take the price_type currency from the product field
                # This is right cause a field cannot be in more than one currency
                res[product.id] = self.pool.get('res.currency').compute(cr, uid, price_type_currency_id,
                                                                        context['currency_id'], res[product.id], context=context)

        return res


class ProductAttributeLine(osv.osv):
    _inherit = "product.attribute.line"
    _order = 'sequence'

    _columns = {
        'sequence': fields.integer('Sequence', help="Determine the display order", required=True),
    }

    def _get_default_sequence(self, cr, uid, context=None):
        # without this function there was a bug when attributes were created
        # from Product Variants tab. If several attributes were created without pushing the save button
        # sequence got the same value for their attribute lines. And if there was no lines before
        # sequence got False for the first attribute
        num = self.search_count(cr, uid, [], context=context) + 1
        return num

    _defaults = {
        'sequence': _get_default_sequence,
    }
