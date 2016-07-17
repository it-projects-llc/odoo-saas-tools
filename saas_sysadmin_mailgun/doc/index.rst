==========================
 Mailgun for saas clients
==========================

Configuration
=============

Amazon Route 53
---------------

* See Amazon Route 53 FAQs here https://aws.amazon.com/route53/faqs/?nc1=h_ls
As suggested in ``Q. How do I get started with Amazon Route 53?`` question you
should first register your domain name.

If you are familiar with DNS then you may register domain
on any other DNS registrator, for example, on https://www.godaddy.com 
and then delegate it to Amazon Route 53.

* install boto - python interface library to Amazon Web Services:

::

 sudo pip install boto


* On http://aws.amazon.com/ create AWS account
* Using this Guide http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html:

 * Create IAM User
 * Note User Security Credentials. Your credentials will look something like this:

  * Access Key ID: AKIAIOSFODNN7EXAMPLE
  * Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

* Grant permissions:

 * Open Users settings on IAM Console https://console.aws.amazon.com/iam/home?#users
 * Choose the user and open ``Permissions`` tab
 * click ``[Attach Policy]`` button
 * In the opened policy list select ``AmazonRoute53DomainsFullAccess`` and ``AmazonRoute53FullAccess`` then click ``[Attach Policy]`` button

Mailgun
-------

* On https://mailgun.com create an account
* Note Secret API key on the main page of your account ``API Keys`` section. It will look something like this: key-ff4518c5a238741da42a291ba6fa77fa

SaaS Portal
-----------

* From menu ``Settings / SaaS Portal Settings`` put your Amazon Access Key ID and Secret Access Key into Amazon access section and click ``[apply]``
* From menu ``Settings > Saas Portal Settings`` put your Mailgun API Key into Mailgun access section and click ``[apply]``
* Open ``SaaS / SaaS / Servers`` and select the saas server where you want to create client databases with mail feature.
Here you should:

 * Click ``[Edit]`` button
 * In ``System Admin Settings`` section fill ``Server IP Address`` field and click ``[Save]``.
 If you want your clients to be able to use Incomming mail feature then there should be public IP address
 of your server.
 If you just want your cliets to be able to send mails then there may be any IP address.

 * Click ``[Edit]`` button
 * In ``System Admin Settings`` section fill ``AWS Hosted Zone`` field

  * Start to type your domain name there
  * Drop-down list will appear
  * Select ``Create and Edit`` there
  * In ``Create: AWS Hosted Zone`` form that will appear fill ``Domain Name`` field
  * Check ``Create Zone`` and click ``[Save]`` button
  * Click ``[Save]`` button

 * You may check that AWS Hosted Zone is created by clicking on it.
 In the opened form check ``Hosted Zone ID`` field. It should look something like this: ``Z1TPJD5TH76P8``
 Also you may check on https://console.aws.amazon.com/route53 that the Hosted Zone is created.


Configuration in template database
----------------------------------

On Portal:

* Open ``SaaS / SaaS / Plans`` and select the Plan where you want mail feature
* Click ``[Log in to template DB]``. You should first allow pop-up windows from SaaS Portal in your browser settings.
  
In template database:

* Activate debug mode
* Open ``Settings / Technical / Email / Outgoing Mail Servers``
* Select ``localhost`` configuration line and delete it using ``[Action]`` button

The steps above guarantee only Outgoing mails.
If you want your clients not only send but receive mails, i.e. Incomming mails,
you should do the following:

* In template database install this module https://github.com/it-projects-llc/mail-addons/tree/9.0/mailgun


Configure mail Aliases for users in client databases
----------------------------------------------------

* Owner of client database or Administrator should configure mail Alias for every user in his database including his own:

 * Open menu ``Settings / Users / Users`` and select User 
 * Click ``[Edit]`` button
 * Open ``Preferences`` tab
 * Edit ``Messaging Alias`` field there


Usage
=====

* Try to create client database as usual
* On creating new client database a new mail domain will be created for it in your account of mailgun.com 
* This mail domain will be validated using Route53, all necessary dns records will be created
* In the client database Outgoing mail configuration will be done
* If you have installed this module https://github.com/it-projects-llc/mail-addons/tree/9.0/mailgun on
template database as mentioned in ``Configuration in template database`` and
configure mail Aliases as mentioned in ``Configure mail Aliases for users in client databases``
of this instruction then your clients will be able receive and send mails
