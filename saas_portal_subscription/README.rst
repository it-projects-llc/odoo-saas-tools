SaaS Portal Subscription
========================

This module helps the management of subscriptions:

* Adds a subscription log of expiration changes and reasons to SaaS clients.
* The expiration date is computed from:

  * SaaS client creation date.
  * Expiration changes.
  * Grace days in plan.
  * Trial hours in plan.
  
* An email is sent to the customer after each expiration change.
