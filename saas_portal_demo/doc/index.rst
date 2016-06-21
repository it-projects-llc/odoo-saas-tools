==================
 Demo datatabases
==================

__demo__.py
===========

Put this in your module folder (i.e. near ``__openerp__.py``).

Use format below (example for `reminder modules<https://apps.odoo.com/apps/modules/category/reminders%20and%20agenda/browse?author=IT-Projects%20LLC>`_)

.. code-block:: python

    # -*- coding: utf-8 -*-
    {
        "title_url": "reminders-and-agenda",
        "title": "Reminders and Agenda",
        "summary": "Set of modules to organise all your tasks, todos, events, etc.",
        "addons_extra_demo":  ["reminder_crm_next_action", "reminder_phonecall"],
        "addons_extra":  ["website"],
    }

* ``"addons_extra_demo"`` - additional addons to be demostrated
* ``"addons_extra"`` - additional addons to be installed, but without noticing in Demo Page

Configuration
=============

SaaS Servers
------------

You need at least one SaaS Server per each odoo version (e.g. server-8, server-9).

* Odoo version can be configured in ``saas_server.odoo_version`` config Paramater


Automatic Plans generation
--------------------------

Open *SaaS Server*

* Open ``SaaS Server / Configuration / Repositories``
* Create new record

  * specify Path
  * Switch ``[x] Publish on website after creating`` off, if you want to check Plan before publishing
  * Switch ``[ ] Show Add To Cart button`` on, if you are going to use Plans to sale databases (e.g. via ``saas_portal_sale_online`` module)

Open *SaaS Portal*
* Open  ``SaaS / SaaS / Servers``

  * Switch to some Server
  * click ``[Update Repositories]``
  * click ``[Restart Server]`` (TODO: do we need it?)
  * click ``[Generate Demo Plans]``

* Open  ``SaaS / SaaS / Plans`` -- you see new plans

Also, you can activate cron task for recurring checking for updates
* Open ``Settings / Technical / Automation / Scheduled Actions``
* Switch to ``Scan for demo databases``
* Click ``[Edit]``
* Switch ``Active`` on
* Click ``[Save]``


Manual creating demo Plans
--------------------------

* Open  ``SaaS / SaaS / Plans``
* Click ``[Create]``

  * specify **Server**
  * specify **Template**
  * specify **Expiration (hours)**
  * specify **Version**
  * At ``Demo Databases`` section

    * add some **Demo modules**

      * **Name**
      * **Technical Name**
      * **Summary**
      * **Image Url**
      * **Icon Url**
      * **Price**
      * **Currency**

* Click ``[Save]``
* Open ``Sale / Products / Products``
* Click ``[Create]``

* Specify **SEO URL**
* Switch ``[ ] Show Add To Cart button`` on if needed
* Open ``Variants`` Tab

  * add Attribute Version
  * add Attribute Values (e.g. 8.0, 9.0)

* Click ``[Save]``
* Click ``[List of Variants]`` smart button
  * Create \ Open some record
  * Specify **Plan for Variant**

Adding demo link to Application
-------------------------------

* Open  ``SaaS / SaaS / Plans`` -> choose some Plan
* Click ``[Demo Page Published]``
* You are navigated to Demo Page. Copy that url
* Use the Url in your application description

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
