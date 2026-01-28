from httpx import post, AsyncClient as HttpxAsyncClient
from time import time
from .exception_handlers import raise_api_exception


class BaseToken:
    """Base class for bKash token management with shared logic."""
    def __init__(self, username: str, password: str, app_key: str, app_secret: str, sandbox=False) -> None:
        self.base_url = "https://tokenized.pay.bka.sh/v1.2.0-beta"
        if sandbox:
            self.base_url = "https://tokenized.sandbox.bka.sh/v1.2.0-beta"
        
        self.username = username
        self.app_key = app_key
        self.timestamp = 0
        self.expires_in = 0
        self.id_token = None
        
        self.headers = {
            "username": username,
            "password": password
        }
        self.data = {
            "app_key": app_key,
            "app_secret": app_secret
        }
    
    def _load_token(self, token: dict) -> None:
        """Load token data into instance variables."""
        self.id_token = token.get("id_token")
        self.timestamp = token.get("timestamp")
        self.expires_in = token.get("expires_in")
    
    def _is_token_valid(self) -> bool:
        """Check if current token is valid."""
        return self.id_token and not (time() - self.timestamp > self.expires_in)
    
    def _process_token_response(self, token_obj: dict) -> dict:
        """Process raw token response from API."""
        raise_api_exception(token_obj)
        token_obj["expires_in"] -= 10  # keeping a 10 seconds overhead
        token_obj["timestamp"] = time()  # adding a key to keep track of when it was fetched
        return token_obj


class Token(BaseToken):
    """Synchronous bKash token manager."""
    
    def _fetch_from_api(self) -> dict:
        """Fetch a new token from the bKash API."""
        response = post(
            url=f"{self.base_url}/tokenized/checkout/token/grant",
            headers=self.headers,
            json=self.data
        )
        response.raise_for_status()
        token_obj = response.json()
        return self._process_token_response(token_obj)
    
    def get_token_id(self) -> str:
        """Gets a valid bKash API token ID.
        
        Returns a cached token if available, otherwise fetches a new one.
        
        Returns:
            str: Valid bKash API token ID
        
        Raises:
            APIError: If token fetch fails
        """
        if self._is_token_valid():
            return self.id_token
        
        token = self._fetch_from_api()
        self._load_token(token)
        return self.id_token
    
    def get_new_token_id(self) -> str:
        """Forces a fresh token fetch from the bKash API.
        
        Returns:
            str: New bKash API token ID
        
        Raises:
            APIError: If token fetch fails
        """
        token = self._fetch_from_api()
        self._load_token(token)
        return self.id_token
    
    def get_headers(self) -> dict:
        """Returns authorization headers for bKash API requests.
        
        Returns:
            dict: Headers with authorization token and X-APP-Key
        
        Raises:
            APIError: If token retrieval fails
        """
        return {
            "authorization": str(self.get_token_id()),
            "X-APP-Key": self.app_key
        }


class AsyncToken(BaseToken):
    """Asynchronous bKash token manager."""
    
    def __init__(self, username: str, password: str, app_key: str, app_secret: str, sandbox=False) -> None:
        super().__init__(username, password, app_key, app_secret, sandbox)
        self._client = HttpxAsyncClient(base_url=self.base_url)
    
    async def aclose(self) -> None:
        """Closes the async HTTP client connection.
        
        Should be called when done using the token manager to clean up resources.
        """
        await self._client.aclose()
    
    async def _fetch_from_api(self) -> dict:
        """Fetch a new token from the bKash API."""
        response = await self._client.post(
            url="/tokenized/checkout/token/grant",
            headers=self.headers,
            json=self.data
        )
        response.raise_for_status()
        token_obj = response.json()
        return self._process_token_response(token_obj)
    
    async def get_token_id(self) -> str:
        """Gets a valid bKash API token ID.
        
        Returns a cached token if available, otherwise fetches a new one.
        
        Returns:
            str: Valid bKash API token ID
        
        Raises:
            APIError: If token fetch fails
        """
        if self._is_token_valid():
            return self.id_token
        
        token = await self._fetch_from_api()
        self._load_token(token)
        return self.id_token
    
    async def get_new_token_id(self) -> str:
        """Forces a fresh token fetch from the bKash API.
        
        Returns:
            str: New bKash API token ID
        
        Raises:
            APIError: If token fetch fails
        """
        token = await self._fetch_from_api()
        self._load_token(token)
        return self.id_token
    
    async def get_headers(self) -> dict:
        """Returns authorization headers for bKash API requests.
        
        Returns:
            dict: Headers with authorization token and X-APP-Key
        
        Raises:
            APIError: If token retrieval fails
        """
        return {
            "authorization": str(await self.get_token_id()),
            "X-APP-Key": self.app_key
        }
