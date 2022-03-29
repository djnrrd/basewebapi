"""Module containing the synchronous BaseWebAPI class
"""
import requests


class BaseWebAPI:
    """Basic class for all HTTP based apis.  This class will provide the basic
    constructor and transaction methods, along with checking HTTP return
    codes. All other API modules should extend this class

    :param hostname: The host name or IP address of the host to query. This
        should not contain any protocols or port numbers
    :param api_user: The username of the API account
    :param api_pass: The password of the API account
    :param secure: (optional): Use an SSL connection instead of plaintext
    :param enforce_cert: (optional): If using SSL, verify that the provided
        certificates are signed with a trusted CA
    :param alt_port: (optional): If the API service is running on a different
        TCP port this can be defined here.
    :cvar api_user: The stored username
    :cvar api_pass: The stored password for the user
    :cvar base_url: The constructed url base, consisting of protocol,
        host and alternate ports where required. Paths to methods will be
        appended to this
    :cvar enforce_cert: If the SSL certificate should be verified against
        locally installed CAs
    :cvar headers: Constructed headers to include with all transactions
    :cvar status_codes: List of acceptable status codes from the API service
    """

    def __init__(self, hostname: str, api_user: str, api_pass: str,
                 secure: bool = False, enforce_cert: bool = False,
                 alt_port: str = '') -> None:
        # Input error checking
        self._input_error_check(**locals())
        self.api_user = api_user
        self.api_pass = api_pass
        if secure:
            self.base_url = f"https://{hostname}"
        else:
            self.base_url = f"http://{hostname}"
        self.enforce_cert = enforce_cert
        if alt_port:
            self.base_url = f"{self.base_url}:{alt_port}"
        self.headers = {}
        self.status_codes = [200]

    @staticmethod
    def _input_error_check(**kwargs) -> None:
        """Check the supplied values are the correct data types"""
        for var in ('hostname', 'api_user', 'api_pass', 'alt_port'):
            if not isinstance(kwargs[var], str):
                raise ValueError(f"{var} must be a string")
        for var in ('secure', 'enforce_cert'):
            if not isinstance(kwargs[var], bool):
                raise ValueError(f"{var} must be a boolean")

    def _transaction(self, method: str, path: str, **kwargs) \
            -> requests.Response:
        """This method is purely to make the HTTP call and verify that the
        HTTP response code is in the accepted list defined in __init__
        be checked by the calling method as this will vary depending on the API.


        :param method: The HTTP method / RESTful verb  to use for this
            transaction.
        :param path: The path to the API object you wish to call.  This is the
            path only starting with the first forward slash , as this function
            will add the protocol, hostname and port number appropriately
        :param kwargs: The collection of keyword arguments that the requests
            module will accept as documented at
            http://docs.python-requests.org/en/master/api/#main-interface
        :return: Requests response object
        :raises: (requests.RequestException, requests.ConnectionError,
            requests.HTTPError, requests.URLRequired,
            requests.TooManyRedirects, requests.ConnectTimeout,
            requests.ReadTimeout)
        """

        kwargs['verify'] = self.enforce_cert
        kwargs['headers'] = self.headers
        url = self.base_url + path
        result = requests.request(method, url, **kwargs)
        if result.status_code not in self.status_codes:
            raise requests.exceptions.HTTPError(f"HTTP Status code "
                                                f"{result.status_code} not in "
                                                f"valid response codes")
        return result
