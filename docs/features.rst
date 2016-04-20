Features
========

* create SaaS Client databases:

  * manually from SaaS Portal backend
  * by client after choosing subdomain (similar to https://www.odoo.com/page/start ) - module saas_portal_start
  * by client after choosing database template (e.g. template for POS, template for ECommerce etc) with auto-generated subdomain (e.g. demo-12345.odoo.com) - module saas_server_templates
  * by client after singing up - module saas_portal_signup
  * by client via Trial button (saas_portal_sale_online)

* prepare templates for new SaaS Client database. You are able to connect to template database, install modules you need, edit configuration, edit access rights for customer etc. Such template database will be exactly what a customer will see after database creating.
* connect to existed SaaS Client database as administrator
* control SaaS Client database from SaaS Portal backend:

  * install, update, delete addons
  * configure parameters (e.g. Max Allowed Users)
  * grant or remove access rights for database users
  * block database (users will be logged out immediately and will not able to log in back until unblocking)
  * rename database (e.g. to change domain name)
  * delete database

* collect information from client databases (count of users, disk space usage, etc.)
* sale subscription (saas_portal_sale, saas_portal_sale_online)
* notify customers about subscription expiration
* control system via external tool (see [api.rst](api.rst))
