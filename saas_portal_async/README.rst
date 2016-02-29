SaaS Portal Asynchronous database creation
==========================================
Asynchronous client database creation.

Attention!
==========
Module does not work on 9.0 because connector ain't ported for 9.0 for this time.

Usage
=====

Prepare enviroment
^^^^^^^^^^^^^^^^^^

Get connector module https://github.com/OCA/connector/tree/8.0

Optionaly you may test connector module using this module: https://github.com/OCA/connector-interfaces/tree/8.0/test_base_import_async

For example try to export/import asyncronous way some contacts.

Directly actions
^^^^^^^^^^^^^^^^

Install this module.


Mark "asynchronous" checkbox when creating new client database from saas plan.

You can look up database creation jobs in Connector->Jobs. If job is done new base is finished.
