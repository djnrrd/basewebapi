import requests
import logging

logging.basicConfig(format='%(asctime)s:%(module)s:%(levelname)s:%(message)s')


class BaseWebAPI(object):
    """Basic class for all HTTP based apis.  This class will provide the basic
    constructor and tranaction methods, along with making sure that the 
    connection to the web server works. All other API modules should extend 
    this class
    
    After running a transaction the lasttrans property will be set to true only
    if there were a successful HTTP transaction. Any HTTP error codes will need
    to be checked by the subclass method and lasttrans updated accordingly
    """

    def __init__(self, hostname, apiuser, apipass, secure=False, enforcecert=False, altport=""):
        """Basic constructor for web apis. While the constructor asks for the 
        usernames and password these should be used by the derived class after 
        calling this constructor as a super.

        Parameters:
        hostname: The host name or IP address of the host to query. This should
            not contain any protocols or port numbers
        apiuser: The username of the API account
        apipass: The password of the API account
        secure (optional): Use an SSL connection instead of plaintext
        enforcecert (optional): If using SSL, verify that the provided
            certificates are signed with a trusted CA
        altport (optional): If the API service is running on a different TCP
            port this can be defined here.
        """

        self.apiuser = apiuser
        self.apipass = apipass

        if secure:
            self.baseurl = f"https://{hostname}"
        else:
            self.baseurl = f"http://{hostname}"
        self.enforcecert = enforcecert

        if altport:
            self.baseurl = f"{self.baseurl}:{altport}"
        self.headers = {}
        self.lasttrans = False
        self.lasterr = ''
        logging.debug(f"Base API created to {self.baseurl} with {self.apiuser}:{self.apipass}")

    def _transaction(self, method, path, **kwargs):
        """This method is purely to make the HTTP call and will fail the 
        transaction on any connection based error. Any HTTP return code should 
        be checked by the calling method as this will vary depending on the API.

        Parameters:
        method: The HTTP method / RESTful verb  to use for this transaction.
        path: The path to the API object you wish to call.  This is the path
            only starting with the first forward slash , as this function will 
            add the protocol, hostname and port number appropriately
        **kwargs: The collection of keyword arguments that the requests module
            will accept as documented at http://docs.python-requests.org/en/master/api/#main-interface
        
        The lasttrans property should be checked to see if the HTTP transaction
        was successful. If so, A requests.response object should be returned if
        successful and the exception if there were any connection errors"""

        kwargs['verify'] = self.enforcecert
        kwargs['headers'] = self.headers
        url = self.baseurl + path
        logging.debug(f"'Calling {url}")
        try:
            r = requests.request(method, url, **kwargs)
            self.lasttrans = True
            logging.debug(r)
            return r
        except Exception as e:
            self.lasttrans = False
            self.lasterr = e
            logging.warning(e)
            return e
