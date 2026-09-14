## Token Caching

The bKash grant token API  must not be called more than twice per hour (3600s).

pybkash fetches a token and reuses it for as long as it is valid/not expired.

There are two ways pybkash caches the token (Both `Token` and `AsyncToken`):

### In-memory (default)

If you omit `redis_url`, the token is stored on that `Token` / `AsyncToken` instance only. It is not shared across processes.

### Redis

Pass `redis_url` when constructing the token class. This is the suggested option for distributed or multi-process systems: every pybkash instance shares the same cached token, so the grant endpoint is called only when a new token is actually required.

```python
from pybkash import Token

token = Token(
    username="your_username",
    password="your_password",
    app_key="your_app_key",
    app_secret="your_app_secret",
    sandbox=True,
    redis_url="redis://localhost:6379/0",
)
```

The same `redis_url` parameter is available on `AsyncToken`.
