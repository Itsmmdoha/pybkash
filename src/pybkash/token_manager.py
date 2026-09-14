from httpx import Client as SyncClient, AsyncClient as HttpxAsyncClient 
from time import time
from .exception_handlers import raise_api_exception

from redis import Redis as SyncRedis
from redis.asyncio import Redis as AsyncRedis
import json

class BaseToken:
    """Base class for bKash token management with shared logic."""
    def __init__(self, username: str, password: str, app_key: str, app_secret: str, sandbox=False, redis_url: None | str = None) -> None:
        self.base_url = "https://tokenized.pay.bka.sh/v1.2.0-beta"
        if sandbox:
            self.base_url = "https://tokenized.sandbox.bka.sh/v1.2.0-beta"

        self.redis_url = redis_url
        self.username = username
        self.app_key = app_key
        self.headers = {
            "username": username,
            "password": password
        }
        self.data = {
            "app_key": app_key,
            "app_secret": app_secret
        }
        self.token_obj = None

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"username='{self.username[:3]}{'*' * (len(self.username) - 3)}', "
            f"app_key='{self.app_key[:4]}{'*' * (len(self.app_key) - 4)}', "
            f"base_url='{self.base_url}', "
            f"redis={'enabled' if self.redis_url else 'disabled'}"
            f")"
        )

    def _process_token_response(self, token_obj: dict) -> dict:
        """Process a raw token response from the API.

        Validates the response, then mutates and returns it: the
        `expires_in` value is reduced by a 100 second safety overhead,
        and a `timestamp` key is added recording when the token was
        fetched (used later to determine expiry).

        Args:
            token_obj: Raw JSON response from the token grant endpoint.

        Returns:
            dict: The same dict, with `expires_in` adjusted and a new
                `timestamp` key added.

        Raises:
            APIError: If the response body indicates an API-level error.
        """
        raise_api_exception(token_obj)
        token_obj["expires_in"] -= 100  # keeping a 100 seconds overhead
        token_obj["timestamp"] = time()  # adding a key to keep track of when it was fetched
        return token_obj

    def _is_token_expired(self, token_obj: dict) -> bool:
        """Check whether a cached token has expired.

        Args:
            token_obj: Token dict previously produced by
                `_process_token_response`, containing `expires_in` and
                `timestamp`.

        Returns:
            bool: True if the token's expiry time has passed, False otherwise.
        """
        expires_at = token_obj["expires_in"] + token_obj["timestamp"]
        if expires_at > time():
            return False
        return True


class Token(BaseToken):
    """Synchronous bKash token manager."""

    def __init__(self, username: str, password: str, app_key: str, app_secret: str, sandbox=False, redis_url: None | str = None) -> None:
        super().__init__(username, password, app_key, app_secret, sandbox, redis_url)

        self.redis = None
        if redis_url:
            self.redis = SyncRedis.from_url(redis_url)

    def _load_to_cache(self, token: dict) -> None:
        """Store token data for later reuse.

        If a Redis URL was configured, the token is persisted to Redis
        (shared and durable across processes/workers). Otherwise it is
        held only as an in-memory instance attribute, which is
        ephemeral and not shared across processes.

        Args:
            token: Processed token dict to store.
        """
        if self.redis:
            self.redis.set("pybkash_token_obj", json.dumps(token))
            return
        self.token_obj = token

    def _get_from_cache(self) -> dict | None:
        """Retrieve previously stored token data, if any.

        Reads from Redis when configured; otherwise reads the
        in-memory instance attribute set by `_load_to_cache`.

        Returns:
            dict | None: The stored token dict, or None if nothing
                has been cached yet.
        """
        if self.redis:
            token_obj = self.redis.get("pybkash_token_obj")
            if not token_obj:
                return
            return json.loads(token_obj)

        return self.token_obj
    
    def _grant_from_api(self, sync_client: SyncClient) -> dict:
        """Fetch a new token from the bKash API.

        Args:
            sync_client: httpx Client used to make the request.

        Returns:
            dict: Processed token data (see `_process_token_response`).

        Raises:
            httpx.HTTPStatusError: If the HTTP response has an error status.
            APIError: If the response body indicates an API-level error.
        """
        response = sync_client.post(
            url=f"{self.base_url}/tokenized/checkout/token/grant",
            headers=self.headers,
            json=self.data,
        )
        response.raise_for_status()
        raise_api_exception(response.json())
        token_obj = response.json()
        return self._process_token_response(token_obj)
    
    def get_token_id(self, sync_client: SyncClient) -> str:
        """Gets a valid bKash API token ID.
        
        Returns a cached token if available, otherwise fetches a new one.

        Args:
            sync_client: httpx Client used to make the request if a
                new token needs to be fetched.
        
        Returns:
            str: Valid bKash API token ID
        
        Raises:
            httpx.HTTPStatusError: If a new token fetch returns an error status.
            APIError: If token fetch fails at the API level.
        """
        token_obj = self._get_from_cache()
        if not token_obj or self._is_token_expired(token_obj):
            token_obj = self._grant_from_api(sync_client)
            self._load_to_cache(token_obj)
            return token_obj["id_token"]

        return token_obj["id_token"]

    def get_headers(self, sync_client: SyncClient) -> dict:
        """Returns authorization headers for bKash API requests.

        Args:
            sync_client: httpx Client used to make the request if a
                new token needs to be fetched.
        
        Returns:
            dict: Headers with authorization token and X-APP-Key

        Raises:
            httpx.HTTPStatusError: If a new token fetch returns an error status.
            APIError: If token fetch fails at the API level.
        """
        return {
            "authorization": str(self.get_token_id(sync_client)),
            "X-APP-Key": self.app_key
        }


class AsyncToken(BaseToken):
    """Asynchronous bKash token manager."""

    def __init__(self, username: str, password: str, app_key: str, app_secret: str, sandbox=False, redis_url: None | str = None) -> None:
        super().__init__(username, password, app_key, app_secret, sandbox, redis_url)

        self.redis = None
        if redis_url:
            self.redis = AsyncRedis.from_url(redis_url)

    async def _load_to_cache(self, token: dict) -> None:
        """Store token data for later reuse.

        If a Redis URL was configured, the token is persisted to Redis
        (shared and durable across processes/workers). Otherwise it is
        held only as an in-memory instance attribute, which is
        ephemeral and not shared across processes.

        Args:
            token: Processed token dict to store.
        """
        if self.redis:
            await self.redis.set("pybkash_token_obj", json.dumps(token))
            return
        self.token_obj = token

    async def _get_from_cache(self) -> dict | None :
        """Retrieve previously stored token data, if any.

        Reads from Redis when configured; otherwise reads the
        in-memory instance attribute set by `_load_to_cache`.

        Returns:
            dict | None: The stored token dict, or None if nothing
                has been cached yet.
        """
        if self.redis:
            token_obj = await self.redis.get("pybkash_token_obj")
            if not token_obj:
                return
            return json.loads(token_obj)

        return self.token_obj

    async def _grant_from_api(self, async_client: HttpxAsyncClient) -> dict:
        """Fetch a new token from the bKash API.

        Args:
            async_client: httpx AsyncClient used to make the request.

        Returns:
            dict: Processed token data (see `_process_token_response`).

        Raises:
            httpx.HTTPStatusError: If the HTTP response has an error status.
            APIError: If the response body indicates an API-level error.
        """
        response = await async_client.post(
            url=f"{self.base_url}/tokenized/checkout/token/grant",
            headers=self.headers,
            json=self.data
        )
        response.raise_for_status()
        raise_api_exception(response.json())
        token_obj = response.json()
        return self._process_token_response(token_obj)

    async def get_token_id(self, async_client: HttpxAsyncClient) -> str:
        """Gets a valid bKash API token ID.
        
        Returns a cached token if available, otherwise fetches a new one.

        Args:
            async_client: httpx AsyncClient used to make the request if
                a new token needs to be fetched.
        
        Returns:
            str: Valid bKash API token ID
        
        Raises:
            httpx.HTTPStatusError: If a new token fetch returns an error status.
            APIError: If token fetch fails at the API level.
        """
        token_obj = await self._get_from_cache()
        if not token_obj or self._is_token_expired(token_obj):
            token_obj = await self._grant_from_api(async_client)
            await self._load_to_cache(token_obj)
            return token_obj["id_token"]

        return token_obj["id_token"]

    async def get_headers(self, async_client: HttpxAsyncClient) -> dict:
        """Returns authorization headers for bKash API requests.

        Args:
            async_client: httpx AsyncClient used to make the request if
                a new token needs to be fetched.
        
        Returns:
            dict: Headers with authorization token and X-APP-Key
        
        Raises:
            httpx.HTTPStatusError: If a new token fetch returns an error status.
            APIError: If token retrieval fails at the API level.
        """
        return {
            "authorization": str(await self.get_token_id(async_client)),
            "X-APP-Key": self.app_key
        }
