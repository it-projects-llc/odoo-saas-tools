Domain names for SaaS
=====================


Before we can use SaaS the domain names should be specified.
Domain names may be specified different ways.
The simpliest way in linux is to add lines on local file /etc/hosts.
But this suits only for testing purposes and only in linux.

If we want our customers to be able to work with our servers through browser then
we need DNS server such as https://www.godaddy.com.

You can find general information about DNS systems here https://www.godaddy.com/help/what-is-dns-665.
And here we can see how to add dns records https://www.godaddy.com/help/manage-dns-for-your-domain-names-680.

We need to add several Type 'A' records on our dns server.

Example:
When Portal, Server and Clients on the same IP we can add the following records.

If Portal is example.com then the record is::

    Type: A

    Name: example.com

    IP: 1.2.3.4

If Server is server-1.example.com and Clients are client-001.example.com, client-002.example.com... We need to add just one record for them::

    Type: A

    Name: *.example.com

    IP: 1.2.3.4
 
 




