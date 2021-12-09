from __future__ import annotations
import aiohttp
import asyncio
from typing import Optional, Type
from types import TracebackType


class AsyncBaseWebAPI(object):
    """Basic class for HTTP based apis.  This class will provide the basic
    constructor and transaction methods, along with checking HTTP return
    codes. All other API modules should extend this class

    :param hostname: The host name or IP address of the host to query. This
        should not contain any protocols or port numbers
    :type hostname: str
    :param api_user: The username of the API account
    :type api_user: str
    :param api_pass: The password of the API account
    :type api_pass: str
    :param secure: (optional): Use an SSL connection instead of plaintext
    :type secure: bool
    :param enforce_cert: (optional): If using SSL, verify that the provided
        certificates are signed with a trusted CA
    :type enforce_cert: bool
    :param alt_port: (optional): If the API service is running on a different
        TCP port this can be defined here.
    :type alt_port: str
    :cvar api_user: The stored username
    :cvar api_pass: The stored password for the user
    :cvar base_url: The constructed url base, consisting of protocol,
        host and alternate ports where required. Paths to methods will be
        appended to this
    :cvar enforce_cert: If the SSL certificate should be verified against
        locally installed CAs
    :cvar headers: Constructed headers to include with all transactions
    """

    def __init__(self, hostname: str, api_user: str, api_pass: str,
                 secure: bool=False, enforce_cert: bool=False,
                 alt_port: str='', basic_auth: bool=False) -> AsyncBaseWebAPI:
        # Input error checking
        self._input_error_check(**locals())
        self.api_user = api_user
        self.api_pass = api_pass
        self.basic_auth = basic_auth
        if secure:
            self.base_url = f"https://{hostname}"
        else:
            self.base_url = f"http://{hostname}"
        self.enforce_cert = enforce_cert
        if alt_port:
            self.base_url = f"{self.base_url}:{alt_port}"
        self.headers = {}
        self.status_codes = [200]
        self._session = None

    def __enter__(self) -> None:
        raise TypeError("Use async with instead")

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType]) -> None:
        pass

    async def __aenter__(self) -> AsyncBaseWebAPI:
        await self.open()
        return self

    async def __aexit__(self,
                        exc_type: Optional[Type[BaseException]],
                        exc_val: Optional[BaseException],
                        exc_tb: Optional[TracebackType]) -> None:
        await self.close()

    async def open(self) -> None:
        if not self._session:
            if self.basic_auth:
                auth = aiohttp.BasicAuth(self.api_user, self.api_pass)
            else:
                auth = None
            self._session = aiohttp.ClientSession(
                                                  auth=auth)

    async def close(self) -> None:
        if self._session:
            try:
                await self._session.close()
            except BaseException as e:
                raise e
            finally:
                self._session = None

    @staticmethod
    def _input_error_check(**kwargs) -> None:
        for x in ('hostname', 'api_user', 'api_pass', 'alt_port'):
            if not isinstance(kwargs[x], str):
                raise ValueError(f"{x} must be a string")
        for x in ('secure', 'enforce_cert', 'basic_auth'):
            if not isinstance(kwargs[x], bool):
                raise ValueError(f"{x} must be a boolean")

    async def _transaction(self, method, path, **kwargs):
        """This method is purely to make the HTTP call and verify that the
        HTTP response code is in the accepted
        be checked by the calling method as this will vary depending on the API.


        :param method: The HTTP method / RESTful verb  to use for this
            transaction.
        :type method: str
        :param path: The path to the API object you wish to call.  This is the
            path only starting with the first forward slash , as this function
            will add the protocol, hostname and port number appropriately
        :type path: str
        :param kwargs: The collection of keyword arguments that the requests
            module will accept as documented at
            http://docs.python-requests.org/en/master/api/#main-interface
        :return: Requests response object
        :rtype: requests.Response
        :raises: (requests.RequestException, requests.ConnectionError,
            requests.HTTPError, requests.URLRequired,
            requests.TooManyRedirects, requests.ConnectTimeout,
            requests.ReadTimeout)
        """

        kwargs['ssl'] = None if self.enforce_cert else False
        kwargs['headers'] = self.headers
        url = self.base_url + path
        async with self._session.request(method, url, **kwargs) as conn:
            return await conn
        #if r.status not in self.status_codes:
        #    raise aiohttp.ClientResponseError(f"HTTP Status code "
        #                                        f"{r.status_code} not in "
        #                                        f"valid response codes")
        #else:
        # return r