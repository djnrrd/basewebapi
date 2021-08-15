from unittest import TestCase, mock
from basewebapi import BaseWebAPI
import requests


# Using Mock to replace requests.request so that we don't go hammering servers
# on the network

def mocked_requests_request(*args, **kwargs):
    ret_obj = mock.Mock(spec=requests.Response)
    if args[0] == 'get' and args[1] == 'http://localhost/':
        ret_obj.status_code = 200
    elif args[0] == 'post':
        ret_obj.status_code = 500
    return ret_obj


class TestBaseWebAPI(TestCase):
    def setUp(self):
        self.good_obj = BaseWebAPI('localhost', 'nouser', 'nopass')
        self.bad_dns_obj = BaseWebAPI('invalid.lan', 'nouser', 'nopass')
        self.conn_refused_obj = BaseWebAPI('localhost', 'nouser', 'nopass',
                                           alt_port='9999')
        self.good_secure_obj = BaseWebAPI('localhost', 'nouser', 'nopass',
                                          secure=True)
        self.good_sec_alt_obj = BaseWebAPI('localhost', 'nouser', 'nopass',
                                           secure=True, alt_port='9999')
        self.good_sec_alt_obj = BaseWebAPI('localhost', 'nouser', 'nopass',
                                           secure=True, alt_port='9999')
        self.bad_status_obj = BaseWebAPI('localhost', 'nouser', 'nopass')

    def test_incorrect_arguments(self):
        self.assertRaises(ValueError, BaseWebAPI, 123, 'nouser', 'nopass')
        self.assertRaises(ValueError, BaseWebAPI, 'localhost', 123, 'nopass')
        self.assertRaises(ValueError, BaseWebAPI, 'localhost', 'nouser', 123)
        self.assertRaises(ValueError, BaseWebAPI, 'localhost', 'nouser',
                          'nopass', secure='Yes')
        self.assertRaises(ValueError, BaseWebAPI, 'localhost', 'nouser',
                          'nopass', secure=True, enforce_cert='Yes')
        self.assertRaises(TypeError, BaseWebAPI, 'localhost', 'nouser',
                          'nopass', secure=True, fake_kwarg='Yes')

    def test_object_creation(self):
        # Make sure object instance is correct
        self.assertIsInstance(self.good_obj, BaseWebAPI)

    def test_url_writes(self):
        # Make sure the URL rewrites work as expected
        self.assertEqual('http://localhost', self.good_obj.base_url)
        self.assertEqual('http://localhost:9999',
                         self.conn_refused_obj.base_url)
        self.assertEqual('https://localhost', self.good_secure_obj.base_url)
        self.assertEqual('https://localhost:9999',
                         self.good_sec_alt_obj.base_url)

    def test_bad_kwarg(self):
        # Make sure that the requests module complains if we supply a bad
        # kwarg to it.  We won't test the valid kwargs as that's their job.
        self.assertRaises(TypeError,
                          self.good_obj._transaction, 'get', '/', mykey='test')

    def test_bad_host(self):
        # Check we get the appropriate error when we put a bad hostname in
        self.assertRaises(requests.exceptions.ConnectionError,
                          self.bad_dns_obj._transaction, 'get', '/')

    def test_refused_connection(self):
        # Check we get the appropriate error if the server refuses the
        # connection
        self.assertRaises(requests.exceptions.ConnectionError,
                          self.conn_refused_obj._transaction, 'get', '/')

    @mock.patch('requests.request', side_effect=mocked_requests_request)
    def test_good_request(self, mock_req):
        # Check we get the appropriate response back from requests, mocked so
        # we don't hammer any network resources
        result = self.good_obj._transaction('get', '/')
        self.assertIsInstance(result, requests.Response)

    @mock.patch('requests.request', side_effect=requests.Timeout)
    def test_timeout(self, mock_req):
        # Check we get the appropriate error back if the connection times
        # out, mocked to get the proper exception back from requests
        self.assertRaises(requests.exceptions.Timeout,
                          self.good_obj._transaction, 'get', '/', timeout=1)

    @mock.patch('requests.request', side_effect=requests.TooManyRedirects)
    def test_redirects(self, mock_req):
        # Check we get the appropriate error back if there are too many
        # redirects, mocked to get the proper exception back from requests
        self.assertRaises(requests.exceptions.TooManyRedirects,
                          self.good_obj._transaction, 'get', '/redirects')

    @mock.patch('requests.request', side_effect=mocked_requests_request)
    def test_status_code(self, mock_req):
        self.assertRaises(requests.exceptions.HTTPError,
                          self.bad_status_obj._transaction, 'post', '/')
