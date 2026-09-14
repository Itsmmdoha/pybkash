## Context Managers

Both clients support the context manager protocol for automatic resource cleanup, so you never need to call `close()` / `aclose()` manually.

### Synchronous

```python
from pybkash import Client, Token

token = Token(
    username="your_username",
    password="your_password",
    app_key="your_app_key",
    app_secret="your_app_secret",
    sandbox=True
)

with Client(token) as client:
    payment = client.create_payment(
        callback_url="https://yoursite.com/callback",
        payer_reference="CUSTOMER001",
        amount=1000
    )
    # Client automatically closes when exiting the block
```

### Asynchronous

```python
import asyncio
from pybkash import AsyncClient, AsyncToken

async def process_payment():
    async_token = AsyncToken(
        username="your_username",
        password="your_password",
        app_key="your_app_key",
        app_secret="your_app_secret",
        sandbox=True
    )

    async with AsyncClient(async_token) as client:
        payment = await client.create_payment(
            callback_url="https://yoursite.com/callback",
            payer_reference="CUSTOMER001",
            amount=1000
        )
        # Client automatically closes when exiting the block

asyncio.run(process_payment())
```
