=============
 Module name
=============

Usage
=====

Add demo repositories
---------------------

* Open ``SaaS Server / Configuration / Repositories``
* Create new record

  * choose the repository from drop-down list of available repositories 

Demo parameters in __openerp__.py for modules
---------------------------------------------

* demo_title
* demo_addons
* demo_addons_hidden
* demo_url 

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

     'demo_title': 'super-puper reminders',
     'demo_addons': ['reminder_phonecall', 'reminder_task_deadline'],
     'demo_addons_hidden': ['website'],
     'demo_url': 'reminders-and-agenda',
 }

Demo modules list initialization
--------------------------------

After appending demo parameters to some module the demo list
should be reinitalized

* From ``Settings / Users / Users`` open admin user's form and activate ``Technical Features`` on it
* reload the page
* After reloading ``Settings / Modules / Update Modules List`` menu item should be available. Click ``Update`` button on it.


