==================
 Demo datatabases
==================

All you need to create demos for your applications in `odoo apps store <https://apps.odoo.com/>`_!

The module extends shop pages:

* Adds list of demostrated modules

  * design is similar to one in apps store + button Buy
  * clicking on each module navigates user to app store

* Adds button ``Get Demo for X.0``.

  * On clicking that page user is asked to login
  * After that he receive an email with a link to fresh database with installed modules.

* Adds note ``Also available for [8.0], ...``

* Allows to hide ``Add To Cart`` button (via ``website_sale_add_to_cart_disable``).

The module depends on ``website_seo_url`` to allow links without id, e.g. ``/shop/product/reminders-and-agenda`` instead of ``/shop/product/reminders-and-agenda-123``. It help to have static urls.

Current version is taken from ``version`` parameter, e.g. ``/shop/product/reminders-and-agenda?version=8.0``

Demo databases are automatically destroyed after 3 hours (configurable).

Technically Page is a Plan (``saas_portal.plan``) and demo databases are duplicates from Plan's template.

Plans and templates are generated based on the information from ``__openerp__.py`` files - see the ``saas_server_demo`` module's documentation
about new demo parameters.

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

Demo: http://runbot.it-projects.info/demo/odoo-saas-tools/10.0

HTML Description: https://apps.odoo.com/apps/modules/10.0/saas_portal_demo/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 10.0 00e169c05a270a0943a74fbeb0a884009946c7cd
