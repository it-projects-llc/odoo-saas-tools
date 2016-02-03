# -*- coding: utf-8 -*-
from openerp.addons.saas_utils import connector, database
from openerp.addons.web.http import request
from openerp import models, fields, api, SUPERUSER_ID
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.models import TransientModel

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
    def create_new_database(self, dbname=None, client_id=None, partner_id=None, user_id=None, notify_user=False,
                            trial=False, support_team_id=None, async=None):
        if async:
          session = ConnectorSession(self._cr, self._uid, self._context)
          job_uuid = async_client_create.delay(session, self._name, self.id, dbname=dbname, client_id=client_id,
                                                partner_id=partner_id, user_id=user_id, notify_user=notify_user,
                                                trial=trial, support_team_id=support_team_id, async=async)
          print 'Async job created and pending. UUID: ' + job_uuid
        else:
            res = super(SaasPortalPlan, self)._create_new_database(dbname=dbname, client_id=client_id,
                                                partner_id=partner_id, user_id=user_id, notify_user=notify_user,
                                                trial=trial, support_team_id=support_team_id, async=async)
            return res
