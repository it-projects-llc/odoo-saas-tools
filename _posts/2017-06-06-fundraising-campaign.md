---
layout:     post
title:      "Fundraising campaign"
subtitle:   "It's a time to make the Greate Updates"
date:       2017-06-06 06:06:06
author:     "Ivan Yelizariev"
header-img: "img/posts/sea-flight-sky-earth.jpg"
comments: true
tags: [ Fundraising ]
---

It was three years ago when I started odoo-saas-tools project with a hope, that it could be useful and interesting system. Very soon me and other people found that it is really so. Two years ago I began to build a team and founded [IT-Projects LLC](https://www.it-projects.info/) company. A lot of work was made since that time on odoo-saas-tools and I want to thank you to all [contributors](https://github.com/it-projects-llc/odoo-saas-tools/graphs/contributors) and our clients who helped to develop this opensource project.

As we worked, we realised more and more things that has to be done to make the system much more robust, scalable and easy to use. But we are not able to implement most of those things due to resource shortage. As we develope an opensource project I believe I have a right to ask community to sponsor it. Any help are welcome. It's not only funds, but also development contribution, documentation improvements, sharing news about the campaing, etc.

Fundraising goal and time frame
======================================

We need to fundraise 80 000 US$ for up to 10 months of work.

We are willing to start just when funds will cover 2 months of work (i.e. 16 000 US$) with a hope to fundraise the rest later. Actually, we have already made some work as *IT-Projects LLC* funded 4 000 US$, but it's only about <a href="{{ site.baseurl }}/blog/welcome-to-new-documentation">new project website and documentation</a>. So, we need at least 12 000 US$ continue.

We have two phases of development:

* Phase #1. Initial release of updates - up to 6 months
* Phase #2. Live testing and further improvements - up to 4 months

Fundraising packages
=========================

To encourage sponsors we have prepared three offers:

**8 000 $US package**.

* Only 5 packages are available at the begining
* It is the only way to get exclusive early deploy after finishing *phase #1*
* One year of service after deploy
* First places at sponsors list

**5 000 $US package**.

* Only 5 packages are available at the begining
* Priority deploy after finishing *phase #2*
* Half year of service after deploy
* Second places at sponsors list

**1 000 $US package**.

* Unlimited packages are available before finishing *phase #1* or before reaching the fundraising goal
* Deploy after finishing *phase #2*
* One month of service after deploy
* Third places at sponsors list

Interested?
=============

Contact as by email: <a href="mailto:saas@it-projects.info">saas@it-projects.info</a>

The Updates
==============

It is the minimal list of updates. We expect to do even more.

* scalable deploy for any load
  * Refactoring: One *SaaS Plan* - Many *SaaS Servers*
  * One *SaaS Server* = One cluster (One load balancer + Many instances + One posgtgres + Few special instances for odoo cron workers)
  * Automatic high load testing
* backuping and restoring
  * Refactor backup system
  * Restore *SaaS Client* from database dump (see [comment on issue #383](https://github.com/it-projects-llc/odoo-saas-tools/issues/383#issuecomment-261453697)
* Green runbot status
* Travis tests
  * Testing *SaaS Plan* for different sets of options
  * Testing payments and expiration of *SaaS Client*
  * Testing signup instances creation
* Documentation: clean up, improvements, updates
* Better *SaaS Plan* experience
  * Switching between payment plans (see [issue #383](https://github.com/it-projects-llc/odoo-saas-tools/issues/383))
* syncronisation between *SaaS Portal* and *SaaS Servers*
  * Server wide requests via rpc
  * Reviewed sync scheme
    * Allow to sync one database ony
* Reviewed expiration date feature
* Support system from client database

Current progress
====================

Fundraising and development progress will be published at this [blog]({{ site.baseurl }}/blog/tags/Fundraising). Some funny animation is available at the [main page]({{ site.baseurl }}/)
