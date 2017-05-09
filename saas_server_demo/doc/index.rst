==================
 SaaS Server Demo
==================

Usage
=====

Add demo repositories
---------------------

Add your Git repositories to the list of the Repositories so
the Portal could know where demo modules are to get information needed to generate demo databases for them.

* Open ``SaaS Server / Configuration / Repositories``
* Create new record

  * choose the repository from drop-down list of available repositories

Parameters in __openerp__.py for demo modules
---------------------------------------------

* demo_title
* demo_addons
* demo_addons_hidden
* demo_url
* demo_summary

The example of __openerp__.py file of ``reminder_base``:

::

 {
    'name': "Reminders and Agenda (technical core)",
    'version': '1.0.4',
    'author': 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'GPL-3',
    'category': 'Reminders and Agenda',
    'website': 'https://twitter.com/yelizariev',
    'price': 9.00,
    'currency': 'EUR',
    'depends': ['calendar'],
    'data': [
       'reminder_base_views.xml',
       ],
    'installable': True,

    'demo_title': 'super-duper reminders',
    'demo_addons': ['reminder_phonecall', 'reminder_task_deadline', 'reminder_hr_recruitment'],
    'demo_addons_hidden': ['website'],
    'demo_url': 'reminders-and-agenda',
    'demo_summary': 'The module provides easy way to configure instant or mail notifications for any supported record with date field.'
 }

Also you can add an image. Put it in the ``./static/description`` with the ``demo_image.png`` name. The Portal uses it in website page from where
customers create their demo.

Demo modules list initialization
--------------------------------

After appending demo parameters to some module the demo list
should be reinitalized

* From ``Settings / Users / Users`` open admin user's form and activate ``Technical Features`` on it
* reload the page
* After reloading ``Settings / Modules / Update Modules List`` menu item should be available. Click ``Update`` button on it.

