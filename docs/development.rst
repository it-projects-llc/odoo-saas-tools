Development
===========

Structure of SaaS system:
-------------------------

* SaaS Portal - main database for control servers and clients, manage client templates and plans.
* SaaS Servers - technical databases to control client databases. SaaS server create, edit, delete databases. Each SaaS Server can be installed on a separate machine (e.g. VPS)
* SaaS Clients - client database to be used by customers. Each SaaS Client is attached to a SaaS Server.

