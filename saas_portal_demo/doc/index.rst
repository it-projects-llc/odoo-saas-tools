==================
 Demo datatabases
==================

Configuration
=============

SaaS Servers
------------

You need at least one SaaS Server per each odoo version (e.g. server-8, server-9).
Install the ``saas_server_demo`` module on your server database.
See in ``saas_server_demo/doc/index.rst`` how to modify ``__openerp__.py`` file for demo modules.
There are new parameters are introduced for demo purposes.

Saas Portal
-----------

There are new buttons introduced on saas_portal.server view.

* Open ``SaaS / SaaS / Servers``

  * click ``[Generate Demo Plans]`` to generate demo plans based on information in ``__openerp__.py`` files in your demo modules on selected server.
  * click ``[Generate Demo Template DBs]`` to create template databases for demonstration sets.
  * click ``[Update Repositories]`` to invoke ``git pull`` command for each repositories that are defined in demo repositories list on your server. See ``saas_server_demo/doc/index.rst`` for additional information.
  * click ``[Restart Server]``. Each time you update demo repositories you shoud restart the servers.

Automatic Plans generation
--------------------------

Open *SaaS Server*

* Open ``SaaS Server / Configuration / Repositories``
* Create new record

  * select the repository from drop-down list of available repositories

Open *SaaS Portal*

* Open  ``SaaS / SaaS / Servers``

  * Switch to some Server
  * check that the right version is in ``Odoo version`` field. The version should look like 8 for odoo 8.0 or 9 for odoo 9.0, etc.
  * click ``[Update Repositories]``
  * click ``[Generate Demo Plans]``
  * click ``[Create Demo Template DBs]``

* Open  ``SaaS / SaaS / Plans`` -- you see new plans. For example, ``Demo 8 Reminders and Agenda (technical core)`` for reminder modules in 8.0 server

Also, you can activate cron task for recurring checking for updates

* Open ``Settings / Technical / Automation / Scheduled Actions``
* Switch to ``Scan for demo databases``
* Click ``[Edit]``
* Switch ``Active`` on
* Click ``[Save]``


Adding demonstration products for online shop
---------------------------------------------

Whenever new demonstrative plan is created the new product for demonstration shop is created also.
For different versions of odoo there will be different product variants, e.g. 8.0, 9.0, etc.

nginx configuration
-------------------

Name conventions

Template databases are named as follows

* ``{demo_url}-template.odoo-8.demo.{saas_domain}`` - for odoo 8.0 databases
* ``{demo_url}-template.odoo-9.demo.{saas_domain}`` - for odoo 9.0 databases
* ``{demo_url}-template.odoo-10.demo.{saas_domain}`` - for odoo 10.0 databases

Here ``{demo_url}`` is a new parameter in ``__openerp__`` specially introduced by ``saas_server_demo`` module for such purposes,
``{saas_domain}`` - is a base saas domain, i.e. ``it-projects.info``

Customer databases are named as follows

* ``{demo_url}-%i.odoo-8.demo.{saas_domain}`` - for odoo 8.0 databases
* ``{demo_url}-%i.odoo-9.demo.{saas_domain}`` - for odoo 9.0 databases
* ``{demo_url}-%i.odoo-10.demo.{saas_domain}`` - for odoo 10.0 databases

, where ``%i`` is a number of demo database

After that, you need to configure proxing to corresponded odoo installation, for example
::

 .odoo-8.demo.it-projects.info -> port 8869, 8872
 .odoo-9.demo.it-projects.info -> port 8969, 8972
 .odoo-10.demo.it-projects.info -> port 8069, 8072

Sample nginx configuration for odoo 8 demo databases

::

 server {
        listen 80;
        server_name .odoo-8.demo.it-projects.info;

        location /longpolling {
            proxy_pass http://127.0.0.1:8872;
        }

        location / {
            proxy_pass http://127.0.0.1:8869;
        }
 }

Workflow
========

* User opens *Demo Page*
* User clicks ``[Get Demo]``
* User is asked to login \ sign up
* On signing up user is asked to specify

  * Name
  * Company Name
  * Email
  * Phone Number (optional)
  * Checkbox: I want to receive notifications about application updates

* In one minute user receives email with a link to demo database
* Demo database is destroyed in specified time
