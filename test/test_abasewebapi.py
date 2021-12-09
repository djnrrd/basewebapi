from unittest import IsolatedAsyncioTestCase
from basewebapi.asyncbaseweb import AsyncBaseWebAPI
import aiohttp
import asyncio


class TestAsyncBaseWebAPI(IsolatedAsyncioTestCase):
    
    def setUp(self) -> None:
        self.context_class = AsyncBaseWebAPI
        self.good_obj = AsyncBaseWebAPI('pokeapi.co', 'nouser', 'nopass',
                                        secure=True)
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

    async def test_context_manager(self):
        async with self.context_class('no_url', 'no_user', 'no_pass') as conn:
            self.assertIsInstance(conn, AsyncBaseWebAPI)
            self.assertIsInstance(conn._session, aiohttp.ClientSession)
        self.assertEqual(conn._session, None)

    async def test_no_context_manager(self):
        conn = self.context_class('no_url', 'no_user', 'no_pass')
        await conn.open()
        self.assertIsInstance(conn, AsyncBaseWebAPI)
        self.assertIsInstance(conn._session, aiohttp.ClientSession)
        await conn.close()
        self.assertEqual(conn._session, None)

    def test_incorrect_arguments(self):
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

    async def test_url_writes(self):
        # Make sure the URL rewrites work as expected
        async with self.good_obj as conn:
            self.assertEqual('https://pokeapi.co', conn.base_url)
        async with self.conn_refused_obj as conn:
            self.assertEqual('http://localhost:9999', conn.base_url)
        async with self.good_secure_obj as conn:
            self.assertEqual('https://localhost', conn.base_url)
        async with self.good_sec_alt_obj as conn:
            self.assertEqual('https://localhost:9999', conn.base_url)

    async def test_good_request(self):
        # Check we get the appropriate response back from requests
        async with self.good_obj as conn:
            result = await self.good_obj._transaction('get',
                                                      '/api/v2/pokemon/mew')
        self.assertIsInstance(result, aiohttp.ClientResponse)
