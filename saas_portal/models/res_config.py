from openerp import models, fields
from openerp.addons.web.http import request
import urllib2
import simplejson


class SaasPortalConfigWizard(models.TransientModel):
    _name = 'saas_portal.config.settings'
    _inherit = 'res.config.settings'

    base_saas_domain = fields.Char('Base SaaS domain')
    dbtemplate = fields.Char('Template database')
    saas_server_list = fields.Char('SaaS server list')

    def get_default_base_saas_domain(self, cr, uid, ids, context=None):
        base_saas_domain = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_portal.base_saas_domain", default=None, context=context)
        if base_saas_domain is None:
            domain = self.pool.get("ir.config_parameter").get_param(cr, uid, "web.base.url", context=context)
            try:
                base_saas_domain = urlparse.urlsplit(domain).netloc.split(':')[0]
            except Exception:
                pass
        return {'base_saas_domain': base_saas_domain or False}

    def set_base_saas_domain(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "saas_portal.base_saas_domain", record.base_saas_domain or '', context=context)

    def get_default_dbtemplate(self, cr, uid, ids, context=None):
        dbtemplate = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_portal.dbtemplate", default=None, context=context)
        return {'dbtemplate': dbtemplate or False}

    def set_dbtemplate(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "saas_portal.dbtemplate", record.dbtemplate or '', context=context)

    def get_default_saas_server_list(self, cr, uid, ids, context=None):
        saas_server_list = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_portal.saas_server_list", default=None, context=context)
        return {'saas_server_list': saas_server_list or False}

    def set_saas_server_list(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "saas_portal.saas_server_list", record.saas_server_list or '', context=context)

    def action_update_stats(self, cr, uid, ids, context=None):
        saas_server_list = self.get_default_saas_server_list(cr, uid, ids, context)['saas_server_list']
        saas_server_list = saas_server_list.split(',')

        scheme = request.httprequest.scheme
        for s in saas_server_list:
            url = '{scheme}://{domain}/saas_server/stats'.format(scheme=scheme, domain=s)
            #req = urllib2.Request(url)
            #req.add_header('content-type', 'application/json')
            data = urllib2.urlopen(url).read()
            data = simplejson.loads(data)
            for r in data:
                r['server'] = s
                id = self.pool['oauth.application'].search(cr, uid, [('client_id', '=', r.get('client_id'))])
                if not id:
                    self.pool['oauth.application'].create(cr, uid, r)
                else:
                    self.pool['oauth.application'].write(cr, uid, id, r)
        return None
