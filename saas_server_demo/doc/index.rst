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
* demo_images

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
    "demo_images": [
        "static/description/icon.png",
        "static/description/mail.png",
        "static/description/notif.png",
        "static/description/event-popup.png",
        "static/description/event-form.png",
        "static/description/calendar-week.png",
        "static/description/calendar-month.png",
        "static/description/calendar-day.png",
        "static/description/admin-tool.png",
        "static/description/add-reminder.png",
    ]
 }

* the first image in the demo_images list will be used as title image for product


Demo modules list initialization
--------------------------------

After appending demo parameters to some module the demo list
should be reinitalized

* From ``Settings / Users / Users`` open admin user's form and activate ``Technical Features`` on it
* reload the page
* After reloading ``Settings / Modules / Update Modules List`` menu item should be available. Click ``Update`` button on it.

