odoo-saas-tools
===============

System to sale and manage odoo databases.

Requirements
============

To start SaaS system you need:

* ubuntu/debian OS
* [installed odoo](https://odoo-development.readthedocs.org/en/latest/install.html)
* [configured nginx](docs/port_80.rst) 
* [installed dependencies](docs/dependencies.rst)
* records in /etc/hosts, if you install it locally, or dns records otherwise:

    > sudo bash -c "python saas.py --print-local-hosts >> /etc/hosts"

Build and run
=============

Execute saas.py script and wait some time

> python saas.py --portal-create --server-create --plan-create --odoo-script=/path/to/openerp-server --odoo-config=/path/to/openerp-server.config

The SaaS system is ready! Try, for example, open start page:

* http://saas-portal-8.local/page/start?plan_id=1

Links
=====

* Features: [docs/features.rst](docs/features.rst)
* API integration: [docs/api.rst](docs/api.rst)
* Development: [docs/development.rst](docs/development.rst)
