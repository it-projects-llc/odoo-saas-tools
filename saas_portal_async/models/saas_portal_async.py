# -*- coding: utf-8 -*-
from odoo import api
from odoo import models
try:
    from odoo.addons.connector.queue.job import job
    from odoo.addons.connector.session import ConnectorSession
except:
    def empty_decorator(func):
        return func
    job = empty_decorator



@job
def async_client_create(session, mself, *args, **kwargs):
    model = session.env[mself].browse(args[0])
    plan_id = model.id
    plan = model.env['saas_portal.plan'].browse(plan_id)
    res = plan._create_new_database(**kwargs)
    client = model.env['saas_portal.client'].browse(res.get('id'))
    client.server_id.action_sync_server()


class SaasPortalPlan(models.Model):
    _inherit = 'saas_portal.plan'

    @api.multi
    def create_new_database(self, async=None, **kwargs):
        if async:
            session = ConnectorSession(self._cr, self._uid, self._context)
            job_uuid = async_client_create.delay(session, self._name, self.id, async=async, **kwargs)
        else:
            res = super(SaasPortalPlan, self)._create_new_database(async=async, **kwargs)
            return res
