from unittest import IsolatedAsyncioTestCase
from basewebapi.asyncbasewebapi import AsyncBaseWebAPI
import aiohttp
import asyncio


class TestAsyncBaseWebAPI(IsolatedAsyncioTestCase):
    
    def setUp(self) -> None:
        # Setup all the coroutines for the different tests
        self.context_class = AsyncBaseWebAPI
        self.good_obj = AsyncBaseWebAPI('localhost', 'nouser', 'nopass')
        self.bad_dns_obj = AsyncBaseWebAPI('invalid.lan', 'nouser', 'nopass')
        self.conn_refused_obj = AsyncBaseWebAPI('localhost', 'nouser', 'nopass',
                                                alt_port='9999')
        self.good_secure_obj = AsyncBaseWebAPI('localhost', 'nouser', 'nopass',
                                               secure=True)
        self.good_sec_alt_obj = AsyncBaseWebAPI('localhost', 'nouser', 'nopass',
                                                secure=True, alt_port='9999')
        self.good_sec_alt_obj = AsyncBaseWebAPI('localhost', 'nouser', 'nopass',
                                                secure=True, alt_port='9999')
        self.bad_status_obj = AsyncBaseWebAPI('localhost', 'nouser', 'nopass')
        self.http_status_obj = AsyncBaseWebAPI('httpstat.us', 'nouser',
                                                'nopass')
        self.basic_auth_obj = AsyncBaseWebAPI('httpbin.org', 'fakeuser',
                                              'nopass', basic_auth=True,
                                              secure=True)

    async def test_context_manager(self) -> None:
        # check that the context manager entry and exit deal with the
        # aiohttp.ClientSession correctly
        async with self.context_class('no_url', 'no_user', 'no_pass') as conn:
            self.assertIsInstance(conn, AsyncBaseWebAPI)
            self.assertIsInstance(conn._session, aiohttp.ClientSession)
        self.assertEqual(conn._session, None)

    async def test_no_context_manager(self) -> None:
        # test that everything gets initiated and closed without using the
        # context manager.
        conn = self.context_class('no_url', 'no_user', 'no_pass')
        await conn.open()
        self.assertIsInstance(conn, AsyncBaseWebAPI)
        self.assertIsInstance(conn._session, aiohttp.ClientSession)
        await conn.close()
        self.assertEqual(conn._session, None)

    def test_incorrect_arguments(self) -> None:
        # Text basic input error handling
        self.assertRaises(ValueError, AsyncBaseWebAPI, 123, 'nouser', 'nopass')
        self.assertRaises(ValueError, AsyncBaseWebAPI, 'localhost', 123, 'nopass')
        self.assertRaises(ValueError, AsyncBaseWebAPI, 'localhost', 'nouser', 123)
        self.assertRaises(ValueError, AsyncBaseWebAPI, 'localhost', 'nouser',
                          'nopass', secure='Yes')
        self.assertRaises(ValueError, AsyncBaseWebAPI, 'localhost', 'nouser',
                          'nopass', secure=True, enforce_cert='Yes')
        self.assertRaises(ValueError, AsyncBaseWebAPI, 'localhost', 'nouser',
                          'nopass', secure=True, enforce_cert=True,
                          alt_port=123)
        self.assertRaises(ValueError, AsyncBaseWebAPI, 'localhost', 'nouser',
                          'nopass', secure=True, enforce_cert=True,
                          alt_port='123', basic_auth='Yes')
        self.assertRaises(TypeError, AsyncBaseWebAPI, 'localhost', 'nouser',
                          'nopass', secure=True, enforce_cert=True,
                          alt_port='123', basic_auth=True, fake_kwarg='Yes')

    async def test_url_writes(self) -> None:
        # Make sure the base_URL rewrites work as expected
        async with self.good_obj as conn:
            self.assertEqual('http://localhost', conn.base_url)
        async with self.conn_refused_obj as conn:
            self.assertEqual('http://localhost:9999', conn.base_url)
        async with self.good_secure_obj as conn:
            self.assertEqual('https://localhost', conn.base_url)
        async with self.good_sec_alt_obj as conn:
            self.assertEqual('https://localhost:9999', conn.base_url)

    async def test_bad_kwarg(self) -> None:
        # Make sure that the aiohttp module complains if we supply a bad
        # kwarg to it.  We won't test the valid kwargs as that's their job.
        async with self.good_obj as conn:
            try:
                result = await conn._transaction('get', '/', mykey='test')
            except BaseException as e:
                self.assertIsInstance(e, TypeError)

    async def test_bad_host(self) -> None:
        # Check we get the appropriate error when we put a bad hostname in
        async with self.bad_dns_obj as conn:
            try:
                result = await conn._transaction('get', '/')
            except BaseException as e:
                self.assertIsInstance(e, aiohttp.ClientConnectorError)

    async def test_refused_connection(self) -> None:
        # Check we get the appropriate error if the server refuses the
        # connection
        async with self.conn_refused_obj as conn:
            try:
                result = await conn._transaction('get', '/')
            except BaseException as e:
                self.assertIsInstance(e, aiohttp.ClientConnectorError)

    async def test_good_request_text(self) -> None:
        # Check we get the appropriate string response
        async with self.http_status_obj as conn:
            result = await conn._transaction('get', '/200')
        self.assertIsInstance(result, str)

    async def test_good_request_json(self) -> None:
        # Check we get the appropriate JSON response back from requests
        async with self.http_status_obj as conn:
            conn.headers = {'Accept': 'application/json'}
            result = await conn._transaction('get', '/200')
        self.assertIsInstance(result, dict)

    async def test_raise_for_status(self) -> None:
        # Test that the ClientResponseError is raised for any status not
        # declared in status_codes
        async with self.http_status_obj as conn:
            try:
                result = await conn._transaction('get', '/401')
            except BaseException as e:
                self.assertIsInstance(e, aiohttp.ClientResponseError)

    async def test_timeout(self) -> None:
        # Reduce aiohttp's timeout settings and request a page to sleep
        # longer than that to test timeouts.
        async with self.http_status_obj as conn:
            timeout = aiohttp.ClientTimeout(total=4)
            try:
                result = await conn._transaction('get', '/200',
                                                 params={'sleep': '5000'},
                                                 timeout=timeout)
            except BaseException as e:
                self.assertIsInstance(e, asyncio.exceptions.TimeoutError)

    async def test_basic_auth(self) -> None:
        # Test a server providing a 401 challenge
        async with self.basic_auth_obj as conn:
            result = await conn._transaction('get',
                                             '/basic-auth/fakeuser/nopass')
            self.assertEqual(result['authenticated'], True)
            self.assertEqual(result['user'], 'fakeuser')
