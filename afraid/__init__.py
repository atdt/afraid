#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    afraid

    A simple client for freedns.afraid.org's dynamic DNS service.

    :copyright: (c) 2011 by Ori Livneh <ori.livneh@gmail.com>
    :license: ICT, see LICENSE for more details.
"""

#  usage: afraid.py [-h] [--daemonize] [--log file] [--interval seconds]
#                   user password [hosts [hosts ...]]
#
#  afraid.org dyndns client
#
#  positional arguments:
#    user
#    password
#    hosts               (deafult: all associated hosts)
#
#  optional arguments:
#    -h, --help          show this help message and exit
#    --daemonize, -d     run in background (default: no)
#    --log file          log to file (default: log to stdout)
#    --interval seconds  update interval, in seconds (default: 600)

import argparse
import hashlib
import logging
import re
import sys
import time

import daemon
import requests

# Set timeout for HTTP requests
timeout = 2

# a basic ipv4 regex pattern
ip_pattern = re.compile(r'[0-9]+(?:\.[0-9]+){3}')

RequestException = requests.RequestException


class ApiError(Exception):
    """Custom exception type for API-related failures"""

    pass


class DnsRecord(object):
    """Represents a dynamic dns record"""

    def __hash__(self):
        """DnsRecord objects hash on their hostname"""
        return hash(self.hostname)

    def __cmp__(self, other):
        """DnsRecord objects compare on their hostname"""
        return cmp(self.hostname, getattr(other, 'hostname', None))

    def __init__(self, hostname, ip, update_url):
        self.hostname = hostname
        self.ip = ip
        self.update_url = update_url

    def __repr__(self):
        return '<DnsRecord: {.hostname}>'.format(self)

    def update(self):
        """Updates remote DNS record by requesting its special endpoint URL"""
        response = requests.get(self.update_url, timeout=timeout)
        match = ip_pattern.search(response.content)

        # response must contain an ip address, or else we can't parse it
        if not match:
            raise ApiError("Couldn't parse the server's response",
                    response.content)

        self.ip = match.group(0)


def get_auth_key(*credentials):
    """Builds an auth key, which is the SHA1 hash of the string 'user|pass'"""
    auth_string = '|'.join(credentials)
    return hashlib.sha1(auth_string).hexdigest()


def get_dyndns_records(login, password):
    """Gets the set of dynamic DNS records associated with this account"""
    params = dict(action='getdyndns', sha=get_auth_key(login, password))
    response = requests.get('http://freedns.afraid.org/api/', params=params, timeout=timeout)
    raw_records = (line.split('|') for line in response.content.split())

    try:
        records = frozenset(DnsRecord(*record) for record in raw_records)
    except TypeError:
        raise ApiError("Couldn't parse the server's response",
                response.content)

    return records


def update_continuously(records, update_interval=600):
    """Update `records` every `update_interval` seconds"""
    while True:
        for record in records:
            try:
                record.update()
            except (ApiError, RequestException):
                pass
        time.sleep(update_interval)


def parse_args(args=None):
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='afraid.org dyndns client')

    ## positional arguments

    parser.add_argument('user')
    parser.add_argument('password')
    parser.add_argument('hosts',
            nargs='*',
            help='(deafult: all associated hosts)',
            default=None
    )

    ## optional arguments

    # should we fork?
    parser.add_argument('--daemonize', '-d',
        action='store_true',
        default=False,
        help='run in background (default: no)',
    )

    # log to a file or stdout
    parser.add_argument('--log',
        help='log to file (default: log to stdout)',
        type=argparse.FileType('w'),
        default=sys.stdout,
        metavar='file'
    )

    # how long to sleep between updates
    parser.add_argument('--interval',
        help='update interval, in seconds (default: 21600)',
        metavar='seconds',
        default=6 * 60 * 60, # 6 hours
        type=int
    )

    return parser.parse_args(args)


def main():
    options = parse_args()

    # configure logging
    logging.basicConfig(
        stream=options.log,
        level=logging.INFO,
        format='%(asctime)s          %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )

    records = get_dyndns_records(options.user, options.password)

    if options.hosts:
        records = frozenset(record for record in records
                if record.hostname in options.hosts)

    # fork & run in background
    if options.daemonize:
        with daemon.DaemonContext():
            update_continuously(records, options.interval)

    else:
        update_continuously(records, options.interval)


if __name__ == '__main__':
    main()
