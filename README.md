odoo-saas-tools
===============

System to sale and manage odoo databases.

Usage
=====

To try SaaS system you need:

* ubuntu/debian OS
* [installed odoo](https://odoo-development.readthedocs.org/en/latest/install.html)
* [configured nginx](docs/port_80.rst) 
* [installed dependencies](docs/dependencies.rst)
* some records in /etc/hosts, if you install it locally

    sudo bash -c "python saas.py --print-local-hosts >> /etc/hosts"

Once everything is done, use saas.py script to prepare and run system. It could take some minutes:

    python saas.py --portal-create --server-create --plan-create --odoo-script=/path/to/openerp-server --odoo-config=/path/to/openerp-server.config

The SaaS system is ready! Try, for example, open start page:

* http://saas-portal-8.local/page/start?plan_id=1

Documentations
==============

* Features: [docs/features.rst](docs/features.rst)
* API integration: [docs/api.rst](docs/api.rst)
* Development: [docs/development.rst](docs/development.rst)
