==================
 Demo datatabases
==================

New parameters in __openerp__.py for demonstraton
=================================================

Put this in your module __openerp__.py file.

Use format below (example for `reminder modules<https://apps.odoo.com/apps/modules/category/reminders%20and%20agenda/browse?author=IT-Projects%20LLC>`_)

.. code-block:: python

    # -*- coding: utf-8 -*-
    {
        "demo_demonstrative": True,
        "demo_url": "reminders-and-agenda",
        "demo_addons":  ["reminder_crm_next_action", "reminder_phonecall"],
        "demo_addons_hidden":  ["website"],
    }

* ``"demo_demonstrative"`` - indicates that database should be created on server to demonstrate this module 
* ``"demo_addons"`` - additional addons to be demostrated
* ``"demo_addons_hidden"`` - additional addons to be installed, but without noticing in Demo Page

Configuration
=============

SaaS Servers
------------

You need at least one SaaS Server per each odoo version (e.g. server-8, server-9).



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

* Open  ``SaaS / SaaS / Plans`` -- you see new plans. For example, ``Demo 8 Reminders and Agenda (technical core)``
for reminder modules in 8.0 server

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
