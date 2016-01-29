odoo-saas-tools
===============

System to sale and manage odoo databases.


Usage
=====

Once you have configured [nginx](docs/port_80.rst) and [install dependencies](docs/dependencies.rst), use the following commands to prepare system for local run and wait few minutes until process is finished

    sudo bash -c "python saas.py --print-local-hosts >> /etc/hosts"

    python saas.py --portal-create --server-create --plan-create --run --odoo-script=/path/to/openerp-server --odoo-config=/path/to/openerp-server.config

Then open start page:

* http://saas-portal-8.0.local/page/start

Documentations
==============

* Features: [docs/features.rst](docs/features.rst)
* API integration: [docs/api.rst](docs/api.rst)
* Development: [docs/development.rst](docs/development.rst)
