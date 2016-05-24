from openerp import api, fields, models, _
import json
from openerp import SUPERUSER_ID, exceptions
from openerp.addons.web.http import request
from openerp.addons.saas_base.exceptions import MaximumDBException, MaximumTrialDBException
import werkzeug

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

    def get_plan(self, plan_id=None):
        domain = [('id', '=', plan_id)]
        plans = self.env['saas_portal.plan'].search(domain)
        if not plans:
            raise exceptions.Warning(_('There is no plan configured'))
        return plans[0]

    @api.model
    def get_all_plans(self):
        plans = self.env['saas_portal.plan'].search([('demo', '=', False), ('template_id', '!=', None), ('server_id', '!=', None)])
        code = None
        value = None
        datas = []
        if plans:
            code = 200
        else:
            code = 401
        for plan in plans:
            datas.append({
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
        return json.dumps({'code': code, 'value': datas})

    @api.model
    def launch_new_instance(self, vals):
        print vals, type(vals)
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
        plan = self.get_plan(plan_val.get('plan_id', 0))
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
        try:
            res = plan.create_new_database(dbname=dbname, user_id=user_id, partner_id=partner_id)
            code = 200
            value = res.get('url')
        except MaximumDBException:
            url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_maximumdb', '/')
            code = 401
            value = 'Maxium size'
            return json.dumps({'code': 401, 'value': value})
        except MaximumTrialDBException:
            url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_maximumtrialdb', '/')
            code = 402
            value = 'Maxium trial beta'
            return json.dumps({'code': code, 'value': value})
        except:
            code = 403
            value = 'Databse already exists'
            return json.dumps({'code': code, 'value': value})
        return json.dumps({'code': code, 'value': value})


class api_logs(models.Model):

    _name = "saas.api.logs"

    name = fields.Char('Method', required=True)
    data = fields.Text('Datas', required=True)
    state = fields.Selection([
        ('new', 'New'),
        ('fail', 'Fail'),
        ('done', 'Done'),
    ], 'State')
