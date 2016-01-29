Client database customization
==============================

The key question of client database customization is how to restrict
administration rights. For example, client users should not be able to
uninstall **saas_client** module, edit ir.confir_parameter records
etc. The simplest solution is don't give to customer access to
administration. To make more flexible configuration, you could install
following modules on SaaS Client databases:

*(some modules are not ported for 8.0. Contribution is welcome)*

* [ir_rule_protected](https://github.com/yelizariev/addons-yelizariev/tree/9.0/ir_rule_protected) - makes impossible for non-superuser admin edit\delete protected ir.rule
* [access_restricted](https://github.com/yelizariev/addons-yelizariev/tree/9.0/access_restricted) - makes impossible for administrator set (and see) more access rights (groups) than he already have. (follow the link for more description)
* [hidden_admin](https://github.com/yelizariev/addons-yelizariev/tree/9.0/hidden_admin) - makes admin (user and partner) invisible
* [access_apps](https://github.com/yelizariev/addons-yelizariev/tree/9.0/access_apps) - allows to have administrators which don't have access to Apps
* [access_settings_menu](https://github.com/yelizariev/addons-yelizariev/tree/9.0/access_settings_menu) - allows to show settings menu for non-admin

