#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import afraid


class DummyHttp(object):
    """Mock `requests` object for testing purposes"""

    def __init__(self):
        self.content = None
        self.requests = []

    reset = __init__

    def prime(self, content):
        self.content = content

    def get(self, *args, **kwargs):
        self.requests.append((args, kwargs))
        return self


class AfraidTestCase(unittest.TestCase):

    dummy_records = (
        ('my.hostname.com', '8.8.8.8', 'http://update.me/?key=foo'),
        ('another.host.io', '8.8.4.4', 'http://update.me/?key=bar'),
    )

    api_response = '\n'.join('|'.join(record) for record in dummy_records)

    def setUp(self):
        self.http = afraid.http = DummyHttp()

    def test_get_auth_key(self):
        key = afraid.get_auth_key('root', 'l33t')
        self.assertEquals(key, '756c1a986a6ab3da4872189510dde23e639b4d1b')

    def test_get_dyndns_record(self):
        self.http.prime(self.api_response)
        records = afraid.get_dyndns_records('wintermute', 'secret')
        self.assertEquals(len(records), 2)

        # validate that the right url was queried
        args, kwargs = self.http.requests.pop()
        self.assertEquals(args, ('http://freedns.afraid.org/api/',))
        self.assertEquals(kwargs, {
            'params': {
                'action': 'getdyndns', 
                'sha': afraid.get_auth_key('wintermute', 'secret'),
            }
        })

        records = {record.hostname: record for record in records}

        for hostname, ip, update_url in self.dummy_records:
            record = records.get(hostname)
            self.assertIsNotNone(record)
            self.assertEquals(record.ip, ip)
            self.assertEquals(record.update_url, update_url)

    def test_argument_parsing(self):
        arg_string = '--interval 10 -d root s3cr3t my.foo.com my.bar.net'
        args = afraid.parse_args(args=arg_string.split())

        self.assertEquals(args.interval, 10)
        self.assertTrue(args.daemonize)
        self.assertEquals(args.hosts, ['my.foo.com', 'my.bar.net'])
        self.assertEquals(args.user, 'root')
        self.assertEquals(args.password, 's3cr3t')


class DnsRecordTestCase(unittest.TestCase):
    def setUp(self):
        self.record = afraid.DnsRecord('localhost', '8.8.8.8', 'abc.com')

    def test_cmp(self):
        # same hostname -> compare as equal
        same_hostname = afraid.DnsRecord('localhost', '8.8.4.4', 'xyz.net')
        self.assertEquals(self.record, same_hostname)

        # different hostname -> compare as unequal
        diff_hostname= afraid.DnsRecord('otherhost', '8.8.8.8', 'abc.com')
        self.assertNotEquals(self.record, diff_hostname)

    def test_hashing(self):
        mapping = {self.record: 'a record!'}
        self.assertIn(self.record, mapping)
        self.assertEquals(mapping[self.record], 'a record!')


if __name__ == '__main__':
    unittest.main()
