from openerp import api, fields, models, _
import json
from openerp.addons.web.http import request
from openerp.addons.saas_base.exceptions import MaximumDBException, MaximumTrialDBException
import logging
import openerp

logger = logging.getLogger(__name__)


class api(models.Model):

    _name = "saas.api"

    def get_config_parameter(self, param):
        config = self.env['ir.config_parameter']
        full_param = 'saas_portal.%s' % param
        parameter = config.get_param(full_param)
        return parameter

    def get_full_dbname(self, dbname):
        if not dbname:
            return None
        full_dbname = '%s.%s' % (dbname, self.get_config_parameter('base_saas_domain'))
        return full_dbname.replace('www.', '')

    def get_plan(self, plan_id):
        domain = [('id', '=', plan_id), ('server_id', '!=', None), ('template_id', '!=', None)]
        plans = self.env['saas_portal.plan'].search(domain)
        if plans:
            return plans[0]
        else:
            return None

    @api.model
    def get_all_plans(self, vals=None):
        log = self.env['saas.api.logs'].create({
            'name': 'get_all_plans',
            'data': vals
        })
        vals = json.loads(vals)
        plans = self.env['saas_portal.plan'].search([('demo', '=', False), ('template_id', '!=', None), ('server_id', '!=', None)])
        code = None
        values = None
        values = []
        if plans:
            code = 200
        else:
            code = 401
        for plan in plans:
            values.append({
                'name': plan.name,
                'summary': plan.summary,
                'template_id': plan.template_id.name,
                'maximum_allowed_dbs_per_partner': plan.maximum_allowed_dbs_per_partner,
                'maximum_allowed_trial_dbs_per_partner': plan.maximum_allowed_trial_dbs_per_partner,
                'max_users': plan.max_users,
                'total_storage_limit': plan.total_storage_limit,
                'block_on_expiration': plan.block_on_expiration,
                'block_on_storage_exceed': plan.block_on_storage_exceed,
                'lang': plan.lang,
            })
        if code == 200:
            log.write({'state': 'done'})
        else:
            log.write({'state': 'fail'})
        return json.dumps({'code': code, 'values': values})

    @api.model
    def launch_new_instance(self, vals):
        logger.info('begin launch_new_instance')
        logger.info(vals)
        log = self.env['saas.api.logs'].create({
            'name': 'get_all_plans',
            'data': vals
        })
        vals = json.loads(vals)
        user_val = vals['user']
        plan_val = vals['plan']
        database_name = vals['database']['name']
        user = self.env['res.users'].search([
            ('login', '=', user_val['login']),
            ('fe_id', '=', user_val['fe_id'])
        ])
        user_id = None
        partner_id = None
        plan = self.get_plan(int(plan_val.get('plan_id', 0) or 0))
        if not user:
            user = self.env['res.users'].create(user_val)
            user_id = user.id
            partner_id = user.partner_id.id
        else:
            user_id = user[0].id
            partner_id = user[0].partner_id.id
        dbname = self.get_full_dbname(database_name)
        code = None
        value = None
        if plan:
            try:
                res = plan.create_new_database(dbname=dbname, user_id=user_id, partner_id=partner_id)
                code = 200
                value = res.get('url')
            except MaximumDBException:
                url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_maximumdb', '/')
                code = 401
                value = 'Maxium size'
            except MaximumTrialDBException:
                url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_maximumtrialdb', '/')
                code = 402
                value = 'Maxium trial beta'
            except:
                code = 403
                value = 'Databse already exists'
        else:
            code = 404
            value = 'have not plan'
        if code == 200:
            log.write({'state': 'done'})
        else:
            log.write({'state': 'fail'})
        logger.info('end launch_new_instance')
        return json.dumps({'code': code, 'value': value})

    #TODO: delete instance
    @api.model
    def delete_instance(self, vals):
        log = self.env['saas.api.logs'].create({
            'name': 'get_all_plans',
            'data': vals
        })
        code = None
        values = None
        client_name = json.loads(vals).get('database_name')
        config_obj = self.env['ir.config_parameter']
        base_saas_domain = config_obj.get_param('saas_portal.base_saas_domain')
        print client_name
        print base_saas_domain
        client = self.env['saas_portal.client'].search([('name', '=', client_name + '.' + base_saas_domain)])
        if not client:
            code = 401
            values = 'database is valid'
            log.write({'state': 'fail'})
        else:
            try:
                for cl in client:
                    cl.delete_database_server()
                code = 200
                values = 'Done'
                log.write({'state': 'done'})
            except:
                code = 403
                values = 'Databse not already exists'
                log.write({'state': 'fail'})
        return json.dumps({'code': code, 'values': values})

    #TODO: execute database
    @api.model
    def execute_instance(self, vals):
        log = self.env['saas.api.logs'].create({
            'name': 'get_all_plans',
            'data': vals
        })
        code = None
        values = None
        vals = json.loads(vals)
        config_obj = self.env['ir.config_parameter']
        base_saas_domain = config_obj.get_param('saas_portal.base_saas_domain')
        client = self.env['saas_portal.client'].search([('name', '=', vals.get('database') + '.' + base_saas_domain)])
        if not client:
            code = 400
            values = 'Database not already exists'
        else:

            payload = {
                # TODO: add configure mail server option here
                'update_addons_list': vals.get('update_addons_list'),
                'update_addons': vals.get('update_addons'),
                'install_addons': vals.get('install_addons'),
                'uninstall_addons': vals.get('uninstall_addons'),
                'access_owner_add': vals.get('access_owner_add'),
                'access_remove': vals.get('access_remove'),
                'fixes': vals.get('fixes'),
                'params': vals.get('params'),
            }
            res = client.upgrade(payload=payload)
            print res
            code = 200
            values = 'Done'
        return json.dumps({'code': code, 'values': values})



class api_logs(models.Model):

    _name = "saas.api.logs"

    name = fields.Char('Method', required=True)
    data = fields.Text('Datas', required=True)
    state = fields.Selection([
        ('new', 'New'),
        ('fail', 'Fail'),
        ('done', 'Done'),
    ], 'State', default='new')
