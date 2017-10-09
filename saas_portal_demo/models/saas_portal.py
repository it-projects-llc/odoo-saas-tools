# -*- coding: utf-8 -*-
from odoo import models, fields, api, SUPERUSER_ID


class SaasPortalPlan(models.Model):
    _inherit = 'saas_portal.plan'

    @api.multi
    def create_new_database(self, **kwargs):
        res = super(SaasPortalPlan, self).create_new_database(**kwargs)
        user_id = kwargs.get('user_id')
        user = user_id and user_id != SUPERUSER_ID and self.env['res.users'].browse(user_id)
        if user:
            user.action_id = self.env.ref('saas_portal_demo.action_open_my_instances').id
        return res
