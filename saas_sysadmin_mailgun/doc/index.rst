==========================
 Mailgun for saas clients
==========================

Usage
=====

* Put Mailgun API Key in Settings > Saas Portal Settings
* On create new client database a new mail domain will be created on mailgun
* Mail domain is validated using dns records through AWS Route53
* In the client database Incoming and Outgoing mail configuration will be done
* To receive mails there should be mail-addons/mail_mailgun module installed in the client database
