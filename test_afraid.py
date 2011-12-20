import unittest
import afraid


class DummyHttp(object):

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
                'sha': '85c62448c530781b9d33490b6b06873e05a1b680'
            }
        })

        records = {record.hostname: record for record in records}

        for hostname, ip, update_url in self.dummy_records:
            record = records.get(hostname)
            self.assertIsNotNone(record)
            self.assertEquals(record.ip, ip)
            self.assertEquals(record.update_url, update_url)


if __name__ == '__main__':
    unittest.main()
