from odoo import api, models


class Module(models.Model):
    _inherit = "ir.module.module"

    @api.model
    def search_read(self, domain=None, *args, **kw):
        params = self.env.context.get("params", {})
        is_executed_from_apps_menu = "action" in params and params["action"] == self.env.ref("base.open_module_tree").id

        if not is_executed_from_apps_menu:
            return super(Module, self).search_read(domain, *args, **kw)

        Config = self.env["ir.config_parameter"].sudo()
        visible_modules = Config.get_param("saas_client.visible_modules", default="").strip().split(",")
        visible_modules = list(filter(bool, visible_modules))
        if not visible_modules:
            return super(Module, self).search_read(domain, *args, **kw)

        if not domain:
            new_domain = [("name", "in", visible_modules)]
        else:
            new_domain = ["&", ("name", "in", visible_modules)] + domain
        return super(Module, self).search_read(new_domain, *args, **kw)
