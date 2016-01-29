# -*- coding: utf-8 -*-
from openerp.addons.saas_utils import connector, database
from openerp.addons.web.http import request
from openerp import models, fields, api, SUPERUSER_ID
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.models import TransientModel

@job
def probetry(session, mself, *args, **kwargs):
    model = session.env[mself].browse(args[0])
    plan_id = model.plan_id.id
    plan = model.env['saas_portal.plan'].browse(plan_id)
    res = plan.create_new_database(dbname=model.name, partner_id=model.partner_id.id, user_id=model.user_id.id,
                                                 notify_user=model.notify_user,
                                                 support_team_id=model.support_team_id.id)
    client = model.env['saas_portal.client'].browse(res.get('id'))
    client.server_id.action_sync_server()

class SaasJob(TransientModel):
    _inherit = 'saas_portal.create_client'
    async_creation = fields.Boolean('Asynchronous', default=False, help='Asynchronous creation of client base')


    @api.multi
    def apply(self):
        if self.async_creation:
            session = ConnectorSession(self._cr, self._uid, self._context)
            job_uuid = probetry.delay(session, self._name, self.id)
            print 'Async job created and pending. UUID: ' + job_uuid
        else:
            super(SaasJob, self).apply()