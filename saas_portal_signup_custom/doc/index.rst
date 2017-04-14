======================================
 Create databases after signup custom
======================================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

* `Enable technical features <https://odoo-development.readthedocs.io/en/latest/odoo/usage/technical-features.html>`__
* Allow external users to sign up

 * Open menu ``Settings >> Configuration >> General Settings``
 * in the ``Portal access`` setting group check ``Allow external users to sign up`` and click ``[Apply]`` button

* Create several plans that uses same template

 * Open menu ``SaaS >> SaaS >> Plans``
 * Click ``[Create]`` button
 * Select ``SaaS Server`` and ``Template`` or create new template
 * Check other settings and clik ``[Save]`` button
 * Do the same steps for the second plan but select the template you have selected for your first plan etc.

* Create product and associate it with saas plans

 * Open menu ``Sales >> Products >> Products``
 * Click ``[Create]`` button
 * Fill ``Product Name`` field
 * On ``SaaS`` tab select one or several plans - one db per each plan will be created
 * Check ``Use as default SaaS product`` if you want this product to be selected as default on the signup form
 * Click ``[Save]`` button

Usage
=====

* Log out from SaaS portal or open portal in incognito window
* Click ``Sign in`` and then ``Sign up``
* Fill the form and click ``[Sign up]`` button
* Databases will be created - one per each plan selected in your product
