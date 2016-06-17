==================
 Demo datatabases
==================

All you need to create demos for your applications in `odoo apps store <https://apps.odoo.com/>`_!

The module creates pages /demo/<odoo_version>/<technical_name> (e.g. /demo/9.0/mail-addons). That page contains list of demostrated modules and button 'Live Preview'. On clicking that page user is asked to login. After that he receive an email with a link to fresh database with installed modules.

Demo databases are automatically destroyed after 3 hours (configurable).

Technically Page is a Plan (``saas_portal.plan``) and demo databases are duplicates from Plan's template.

Plans and database templates and  are generated automatically from ``__demo__.py`` files in the root of modules, but could be created manually too.

Credits
=======

Contributors
------------
* Ivan Yelizariev <yelizariev@it-projects.info>

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`_

Further information
===================

Demo: http://runbot.it-projects.info/demo/odoo-saas-tools/9.0

HTML Description: https://apps.odoo.com/apps/modules/9.0/saas_portal_demo/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 8.0 bdf93910c324b17033f6215e217a0d13a64d2456
