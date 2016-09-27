# -*- coding: utf-8 -*-
import requests
import os
import string


def random_password(length=10):
    chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
    password = ''
    for i in range(length):
        password += chars[ord(os.urandom(1)) % len(chars)]
    return password


def add_domain(api_key=None, domain_name=None, smtp_password=None):
    """Adding a domain.
    Sample response:

{
  "domain": {
    "name": "example.com",
    "created_at": "Fri, 22 Nov 2013 18:42:33 GMT",
    "wildcard": false,
    "spam_action": "disabled",
    "smtp_login": "postmaster@example.com",
    "smtp_password": "thiswontwork",
    "state": "active"
  },
  "receiving_dns_records": [
    {
      "priority": "10",
      "record_type": "MX",
      "valid": "valid",
      "value": "mxa.mailgun.org"
    },
    {
      "priority": "10",
      "record_type": "MX",
      "valid": "valid",
      "value": "mxb.mailgun.org"
    }
  ],
  "message": "Domain has been created",
  "sending_dns_records": [
    {
      "record_type": "TXT",
      "valid": "valid",
      "name": "example.com",
      "value": "v=spf1 include:mailgun.org ~all"
    },
    {
      "record_type": "TXT",
      "valid": "valid",
      "name": "k1._domainkey.example.com",
      "value": "k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4G...."
    },
    {
      "record_type": "CNAME",
      "valid": "valid",
      "name": "email.example.com",
      "value": "mailgun.org"
    }
  ]
}

    Adding a domain."""
    return requests.post(
        "https://api.mailgun.net/v3/domains",
        auth=("api", api_key),
        data={'name': domain_name, 'smtp_password': smtp_password})


def get_domains(api_key=None):
    """Get a list of all domains.
    Sample response:

{
  "total_count": 1,
  "items": [
    {
      "created_at": "Wed, 10 Jul 2013 19:26:52 GMT",
      "smtp_login": "postmaster@samples.mailgun.org",
      "name": "samples.mailgun.org",
      "smtp_password": "4rtqo4p6rrx9",
      "wildcard": true,
      "spam_action": "disabled",
      "state": "active"
    }
  ]
}

    Get a list of all domains."""
    return requests.get(
        "https://api.mailgun.net/v3/domains",
        auth=("api", api_key),
        params={"skip": 0,
                "limit": 3})


def get_domain(api_key=None):
    """Get a single domain.
    Sample response:

{
  "domain": {
    "created_at": "Wed, 10 Jul 2013 19:26:52 GMT",
    "smtp_login": "postmaster@domain.com",
    "name": "domain.com",
    "smtp_password": "4rtqo4p6rrx9",
    "wildcard": false,
    "spam_action": "tag",
    "state": "active"
  },
  "receiving_dns_records": [
    {
      "priority": "10",
      "record_type": "MX",
      "valid": "valid",
      "value": "mxa.mailgun.org"
    },
    {
      "priority": "10",
      "record_type": "MX",
      "valid": "valid",
      "value": "mxb.mailgun.org"
    }
  ],
  "sending_dns_records": [
    {
      "record_type": "TXT",
      "valid": "valid",
      "name": "domain.com",
      "value": "v=spf1 include:mailgun.org ~all"
    },
    {
      "record_type": "TXT",
      "valid": "valid",
      "name": "domain.com",
      "value": "k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUA...."
    },
    {
      "record_type": "CNAME",
      "valid": "valid",
      "name": "email.domain.com",
      "value": "mailgun.org"
    }
  ]
}

    Get a single domain."""
    return requests.get(
        "https://api.mailgun.net/v3/domains/YOUR_DOMAIN_NAME",
        auth=("api", api_key))


def delete_domain(api_key=None, domain=None):
    """Deleting a domain.
    Sample response:

{
  "message": "Domain has been deleted"
}

    """
    return requests.delete(
        "https://api.mailgun.net/v3/domains/%s" % domain,
        auth=("api", api_key))


def get_credentials(api_key, domain):
    """Listing all SMTP credentials.
    Sample response:

{
  "total_count": 2,
  "items": [
    {
      "size_bytes": 0,
      "created_at": "Tue, 27 Sep 2011 20:24:22 GMT",
      "mailbox": "user@samples.mailgun.org"
      "login": "user@samples.mailgun.org"
    },
    {
      "size_bytes": 0,
      "created_at": "Thu, 06 Oct 2011 10:22:36 GMT",
      "mailbox": "user@samples.mailgun.org"
      "login": "user@samples.mailgun.org"
    }
  ]
}

    Listing all SMTP credentials."""
    return requests.get(
        "https://api.mailgun.net/v3/domains/%s/credentials" % domain,
        auth=("api", api_key))


def create_credentials(api_key=None, domain=None):
    return requests.post(
        "https://api.mailgun.net/v3/domains/YOUR_DOMAIN_NAME/credentials",
        auth=("api", "YOUR_API_KEY"),
        data={"login": "alice@YOUR_DOMAIN_NAME",
              "password": "secret"})


def create_store_route(api_key=None, domain=None, mail_domain=None, request_scheme='http'):
    """Create a route for message storing and notification"""
    action = "store(notify='%s://%s/mailgun/notify')" % (request_scheme, domain)
    expression = "match_recipient('.*@%s')" % mail_domain
    return requests.post(
        "https://api.mailgun.net/v3/routes",
        auth=("api", api_key),
        data={"priority": 0,
              "description": "odoo mailgun",
              "expression": expression,
              "action": [action]})
