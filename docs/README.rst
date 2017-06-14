======================
 Odoo Saas Tools Docs
======================

https://odoo-saas-tools.readthedocs.io/

How to update Docs
==================

Initialization
--------------

* Fork this repo
* Clone to your machine
* Install dependencies::

    sudo pip install -r requirements.txt

Contribution
------------

* Edit files in the repo. Check documentations:

  * http://www.sphinx-doc.org/en/stable/rest.html
  * http://www.sphinx-doc.org/en/stable/domains.html
  * http://www.sphinx-doc.org/en/stable/markup/index.html

* Try it out::

    cd /path/to/odoo-saas-tools/docs
    make html
    # check warningn and errors in compilation logs
    google-chrome _build/html/index.html

* Make commits, push, create Pull Request
