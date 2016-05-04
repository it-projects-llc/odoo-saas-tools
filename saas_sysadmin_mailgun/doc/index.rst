==========================
 Mailgun for saas clients
==========================

Usage
=====

* Get your Amazon AWS credentials http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html
* In Amazon IAM Console menu IAM / Users / <your user>, tab Permissions click ``[Attach Policy]``, select 'AmazonRoute53DomainsFullAccess' and 'AmazonRoute53FullAccess'
* From menu ``Settings / SaaS Portal Settings`` put your Amazon Access Key ID and Secret Access Key into Amazon access section and click ``[apply]``
* Get your Mailgun credentials
* From menu ``Settings > Saas Portal Settings`` put your Mailgun API Key into Mailgun access section and click ``[apply]``
* On creating new client database a new mail domain will be created for it on mailgun
* This mail domain will be validated using Route53, all necessary dns records will be created
* In the client database Outgoing mail configuration will be done
* To receive mails there should be mail-addons/mail_mailgun module installed in the client database
