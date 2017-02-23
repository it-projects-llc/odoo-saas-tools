[![Build Status](http://runbot.it-projects.info/runbot/badge/flat/odoo-saas-tools/10.0.svg)](http://runbot.it-projects.info/demo/odoo-saas-tools/10.0)

odoo-saas-tools
===============

System to sale and manage odoo databases.

Requirements
============

To start SaaS system you need:

* ubuntu/debian OS
* [installed odoo](http://odoo-development.readthedocs.io/en/latest/admin/install.html)
* [configured nginx](docs/port_80.rst) 
* [installed dependencies](docs/dependencies.rst)
* [correctly configured odoo](docs/odoo-configuration.rst) 
* records in /etc/hosts, if you install it locally, or dns records otherwise:

    > sudo bash -c "python saas.py --print-local-hosts >> /etc/hosts"

Build and run
=============

Execute saas.py script and wait some time

> python saas.py --portal-create --server-create --plan-create --run --odoo-script=/path/to/odoo-bin --odoo-config=/path/to/odoo-server.config

The SaaS system is ready! Try, for example, open start page:

* http://saas-portal-9.local/page/start?plan_id=1

Links
=====

* Features: [docs/features.rst](docs/features.rst)
* API integration: [docs/api.rst](docs/api.rst)
* Development: [docs/development.rst](docs/development.rst)
