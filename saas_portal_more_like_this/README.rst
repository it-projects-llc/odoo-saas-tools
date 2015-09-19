SaaS Portal More Like This
==========================

Module allows you to provision a client instance that is an exact replica of 
another existing client.

The reason for this being that it is not uncommon for clients instance to evolve
far beyond the template on which they are based. And so this allows you to 
provision an identical instance in seconds rather than have to re-appply all your
changes to the template. 

This module is very useful in cases in which you wish to provide a training 
environment for a client based on the exact copy of their live instance

Notes
-----

* please not that this copies over the entire DB and not just configuration and so should not be used to provision new client... use templates instead as that is what they are for
