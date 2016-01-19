# -*- coding: utf-8 -*-
# import openerp
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request

# import werkzeug
# import simplejson
# import uuid
# import random
import logging


_logger = logging.getLogger(__name__)


class SaasPricing(http.Controller):

    @http.route('/saas/pricing/payment/validate', type='http', auth="public",
                website=True)
    def payment_validate(self, sale_order_id=None, **post):
        redirect = post.get("r", False)

        _logger.info(
            "\n\nReceived Payment Feedback with [sale_id: %s] and [post: %s]\n",
            sale_order_id, post)

        cr, uid, context = request.cr, request.uid, request.context
        email_act = None
        sale_order_obj = request.registry['sale.order']
        # transaction_obj = request.registry.get('payment.transaction')
        saas_plan_obj = request.registry['saas_portal.plan']
        plan = saas_plan_obj.browse(cr, uid, int(post['plan_id']))

        if sale_order_id is None:
            order = plan.get_sale_order(int(post['p']), post['d'], False)
        else:
            order = request.registry['sale.order'].browse(cr, SUPERUSER_ID,
                                                          sale_order_id,
                                                          context=context)

        tx = order.payment_tx_id
        _logger.info("\n\nOrder Tx: %s\n", tx)

        # if not order or (order.amount_total and not tx):
        #     return request.redirect(redirect)

        if (not order.amount_total and not tx) or tx.state in ['pending',
                                                               'done']:
            if not order.amount_total and not tx:
                # Orders are confirmed by payment transactions,
                # but there is none for free orders,
                # (e.g. free events), so confirm immediately
                order.action_button_confirm()
            # send by email
            email_act = sale_order_obj.action_quotation_send(cr, SUPERUSER_ID,
                                                             [order.id],
                                                             context=context)
        elif tx and tx.state == 'cancel':
            # cancel the quotation
            sale_order_obj.action_cancel(cr, SUPERUSER_ID, [order.id],
                                         context=context)

        # send the email
        if email_act and email_act.get('context'):
            composer_obj = request.registry['mail.compose.message']
            composer_values = {}
            email_ctx = email_act['context']
            template_values = [
                email_ctx.get('default_template_id'),
                email_ctx.get('default_composition_mode'),
                email_ctx.get('default_model'),
                email_ctx.get('default_res_id'),
            ]
            composer_values.update(
                composer_obj.onchange_template_id(cr, SUPERUSER_ID, None,
                                                  *template_values,
                                                  context=context).get('value',
                                                                       {}))
            if not composer_values.get(
                    'email_from') and uid == request.website.user_id.id:
                composer_values[
                    'email_from'] = request.website.user_id.company_id.email
            composer_id = composer_obj.create(cr, SUPERUSER_ID, composer_values,
                                              context=email_ctx)
            composer_obj.send_mail(cr, SUPERUSER_ID, [composer_id],
                                   context=email_ctx)

        # clean context and session, then redirect to the confirmation page
        # request.website.sale_reset(context=context)

        if redirect:
            return request.redirect(redirect)

    @http.route([
        '/saas/pricing/payment/transaction/<int:acquirer_id>/<string:order_name>'],
        type='json', auth="public", website=True)
    def payment_transaction(self, acquirer_id, order_name):
        cr, uid, context = request.cr, request.uid, request.context
        transaction_obj = request.registry.get('payment.transaction')
        order_obj = request.registry.get('sale.order')

        order_domain = [('name', '=', order_name)]
        candidates = order_obj.search(cr, SUPERUSER_ID, order_domain, context=context)
        order_id = candidates and candidates[0]
        order = order_obj.browse(cr, SUPERUSER_ID, order_id, context=context)

        tx_domain = [('sale_order_id', '=', order_id),
                     ('state', 'not in', ['cancel', 'done'])]
        candidates = transaction_obj.search(cr, SUPERUSER_ID, tx_domain, context=context)
        tx_id = candidates and candidates[0]

        if tx_id:
            tx = transaction_obj.browse(cr, SUPERUSER_ID, tx_id, context=context)
            if tx.state == 'draft':
                tx.write({
                    'acquirer_id': acquirer_id,
                })
            tx_id = tx.id
        else:
            tx_id = transaction_obj.create(cr, SUPERUSER_ID, {
                'acquirer_id': acquirer_id,
                'type': 'form',
                'amount': order.amount_total,
                'currency_id': order.pricelist_id.currency_id.id,
                'partner_id': order.partner_id.id,
                'partner_country_id': order.partner_id.country_id.id,
                'reference': order.name,
                'sale_order_id': order.id,
            }, context=context)

        # update quotation
        request.registry['sale.order'].write(
            cr, SUPERUSER_ID, [order.id], {
                'payment_acquirer_id': acquirer_id,
                'payment_tx_id': tx_id
            }, context=context)

        return tx_id
