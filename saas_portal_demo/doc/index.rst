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
        "technical_name": "reminders",
        "title": "Reminders and Agenda",
        "summary": "Set of modules to organise all your tasks, todos, events, etc.",
        "addons_extra":  ["reminder_crm_next_action", "reminder_phonecall"],
    }

Configuration
=============

Automatic Plans generation
--------------------------

* Open ``SaaS / Configuration / Demo Database / Addons Path``
* Create new record

  * specify Odoo version
  * specify Path -- comma separated list of paths, where modules with ``__demo__.py`` can be found
  * click ``[Generate Plans]``

* Open  ``SaaS / SaaS / Plans`` -- you see new plans

Manual creating demo Plans
--------------------------

* Open  ``SaaS / SaaS / Plans``
* Click ``[Create]``

  * specify **Technical Name**
  * specify **Expiration (hours)**
  * specify **Version**

  * At ``Demo Databases`` section

    * switch **Demo Page Enabled** on
    * specify **Demo Title**
    * specify **Demo Summary**
    * add some **Demo modules**

      * **Name**
      * **Summary**
      * **Image Url**
      * **Icon Url**
      * **Price**
      * **Currency**

Adding demo link to Application
-------------------------------

* Open  ``SaaS / SaaS / Plans`` -> choose some Plan
* Click ``[Demo Page Published]``
* You are navigated to Demo Page. Copy that url
* Use the Url in your application description

Workflow
========

* User opens *Demo Page Url*
* User is navigate to Demo Page
* User clicks ``[Live Preview]``
* User is asked to login \ sign up
* On signing up user is asked to specify

  * Name
  * Company Name
  * Email
  * Phone Number (optional)
  * Checkbox: I want to receive notifications about application updates

* In one minute user receives email with a link to demo database
* Demo database is destroyed in specified time
