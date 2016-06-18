==================
 Demo datatabases
==================

All you need to create demos for your applications in `odoo apps store <https://apps.odoo.com/>`_!

The module extends shop pages:

* Adds list of demostrated modules

  * design is similar to one in apps store + button Buy
  * clicking on each module navigates user to app store

* Adds button ``Get Demo``.

  * On clicking that page user is asked to login
  * After that he receive an email with a link to fresh database with installed modules.

* Allows to hide ``Add To Cart`` button.

The module depends on ``website_seo_url`` to allow links without id, e.g. ``/shop/product/reminders-and-agenda`` instead of ``/shop/product/reminders-and-agenda-123``. It help to have static urls.

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
