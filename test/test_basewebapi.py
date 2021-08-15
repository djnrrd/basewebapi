from unittest import TestCase, mock
from basewebapi import basewebapi
import requests


# Using Mock to replace requests.request so that we don't go hammering servers
# on the network

def mocked_requests_request(*args, **kwargs):
    if args[0] == 'get' and args[1] == 'http://localhost/':
        return mock.Mock(spec=requests.Response)


class TestBaseWebAPI(TestCase):
    def setUp(self):
        self.good_obj = basewebapi.BaseWebAPI('localhost', 'nouser', 'nopass')
        self.bad_dns_obj = basewebapi.BaseWebAPI('invalid.lan', 'nouser',
                                                 'nopass')
        self.conn_refused_obj = basewebapi.BaseWebAPI('localhost', 'nouser',
                                                      'nopass', alt_port='9999')
        self.good_secure_obj = basewebapi.BaseWebAPI('localhost', 'nouser',
                                                     'nopass', secure=True)
        self.good_sec_alt_obj = basewebapi.BaseWebAPI('localhost', 'nouser',
                                                      'nopass', secure=True,
                                                      alt_port='9999')

    def test_object_creation(self):
        self.assertIsInstance(self.good_obj, basewebapi.BaseWebAPI)

    def test_url_writes(self):
        self.assertEqual('http://localhost', self.good_obj.base_url)
        self.assertEqual('http://localhost:9999',
                         self.conn_refused_obj.base_url)
        self.assertEqual('https://localhost', self.good_secure_obj.base_url)
        self.assertEqual('https://localhost:9999',
                         self.good_sec_alt_obj.base_url)

    def test_bad_kwarg(self):
        self.assertRaises(TypeError,
                          self.good_obj._transaction, 'get', '/', mykey='test')

    def test_bad_host(self):
        self.assertRaises(requests.exceptions.ConnectionError,
                          self.bad_dns_obj._transaction, 'get', '/')

    def test_refused_connection(self):
        self.assertRaises(requests.exceptions.ConnectionError,
                          self.conn_refused_obj._transaction, 'get', '/')

    @mock.patch('requests.request', side_effect=mocked_requests_request)
    def test_good_request(self, mock_req):
        result = self.good_obj._transaction('get', '/')
        self.assertIsInstance(result, requests.Response)

    @mock.patch('requests.request', side_effect=requests.Timeout)
    def test_timeout(self, mock_req):
        self.assertRaises(requests.exceptions.Timeout,
                          self.good_obj._transaction, 'get', '/', timeout=1)

    @mock.patch('requests.request', side_effect=requests.TooManyRedirects)
    def test_redirects(self, mock_req):
        self.assertRaises(requests.exceptions.TooManyRedirects,
                          self.good_obj._transaction, 'get', '/redirects')
