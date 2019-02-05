from requests import Session

from uuid import uuid4
from base64 import b64encode
import hashlib
import datetime

from adobe_analytics.config import LOGIN_URL
from adobe_analytics.exceptions import AuthorizationError
from adobe_analytics.adapters import SSLContextAdapter

class OmnitureSession:
    def __init__(self, username=None, secret=None, company=None,
                 api_version=None, proxies=None, timeout=None):
        
        # Due to Adobe's API docs _telling_ you to use username:company
        # as your username, accept both methods of input
        if company:
            self.username = '{}:{}'.format(username, company)
        else:
            self.username = username
        self.proxies = proxies
        self.timeout = timeout
        self.session = Session()

        self.default_headers = self._generate_wsse_header()

        if self.proxies:
            self.session.proxies.update(self.proxies)
        
        # Get SSL Context from OS defaults
        adapter = SSLContextAdapter()
        # Set connection adapters to only accept login by default
        self.session.mount(BASE_URL, adapter)
        
        # Ensure successful login
        response = self.session.get(
            BASE_URL,
            params={'method':'Company.GetEndpoint'},
            headers=self.headers)

        response.raise_for_status()

        r = response.json()
        
        if 'error' in r:
            raise ApiError(r)
        else:
            self.base_url = r
    
    def _generate_wsse_header(self):
        # Adapted from Adobe's analytics-1.4-apis documentation
        # docs/authentication/using_web_service_credentials.md
        nonce = str(uuid4())
        created = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S z')

        sha = sha1((nonce + created + self.secret).encode())
        digest = b64encode(sha.digest()).decode()
        b64nonce = b64encode(nonce.encode()).decode()

        header = 'UsernameToken Username="{username}", '
                 'PasswordDigest="{digest}", '
                 'Nonce="{nonce}", Created="{created}"'
        header = header.format(
            username=self.username, 
            digest=digest, 
            nonce=b64nonce, 
            created=created
        )

        return {'X-WSSE': header}

