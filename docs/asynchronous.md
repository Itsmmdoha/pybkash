## Asynchronous Client

The asynchronous client provides the same functionality as the synchronous client but uses `async/await` for non-blocking operations. This is ideal for web applications and services that handle multiple concurrent requests.

### Initialization

See [Token Caching](token-caching.md) for in-memory vs Redis cache.

```python
import asyncio
from pybkash import AsyncClient, AsyncToken

async_token = AsyncToken(
    username="your_username",
    password="your_password",
    app_key="your_app_key",
    app_secret="your_app_secret",
    sandbox=True  # Optional, default is False for production
)

client = AsyncClient(
    async_token,
    timeout=10,  # Optional, default timeout is 10s
    max_connections=50,  # Optional, max concurrent connections. Defaults to 50.
    max_keepalive_connections=20,  # Optional, max idle connections to keep. Defaults to 20.
    keepalive_expiry=20.0  # Optional, idle connection expiry time in seconds. Defaults to 20.0.
)
```

### Using Async Methods

All methods in `AsyncClient` mirror their synchronous counterparts but must be **awaited**. The method signatures, parameters, and return types are identical.

**Available async methods:**
- `await client.create_payment(...)`
- `await client.execute_payment(...)`
- `await client.query_payment(...)`
- `await client.create_agreement(...)`
- `await client.execute_agreement(...)`
- `await client.query_agreement(...)`
- `await client.cancel_agreement(...)`
- `await client.execute_refund(...)`
- `await client.search_trx(...)`
- `await client.aclose()`  # Note: use `aclose()` instead of `close()`

### Complete Async Payment Example

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
    client = AsyncClient(async_token)
    
    try:
        payment = await client.create_payment(
            callback_url="https://yoursite.com/callback",
            payer_reference="CUSTOMER001",
            amount=1000
        )
        
        execution = await client.execute_payment(payment.payment_id)
        
        if execution.is_complete():
            print(f"Payment successful! TrxID: {execution.trx_id}")
            
    finally:
        await client.aclose()

asyncio.run(process_payment())
```

### Using with Web Frameworks

**FastAPI Example:**
```python
from fastapi import FastAPI
from pybkash import AsyncClient, AsyncToken

app = FastAPI()

async_token = AsyncToken(
    username="your_username",
    password="your_password",
    app_key="your_app_key",
    app_secret="your_app_secret",
    sandbox=True
)
client = AsyncClient(async_token)

@app.post("/create-payment")
async def create_payment(amount: int, payer_ref: str):
    payment = await client.create_payment(
        callback_url="https://yoursite.com/callback",
        payer_reference=payer_ref,
        amount=amount
    )
    return {"payment_id": payment.payment_id, "bkash_url": payment.bkash_url}

@app.on_event("shutdown")
async def shutdown():
    await client.aclose()
```

**Flask Example:**
```python
from flask import Flask, jsonify, request
from pybkash import Client, Token

app = Flask(__name__)

token = Token(
    username="your_username",
    password="your_password",
    app_key="your_app_key",
    app_secret="your_app_secret",
    sandbox=True
)
client = Client(token)

@app.route("/create-payment", methods=["POST"])
def create_payment():
    data = request.get_json()
    payment = client.create_payment(
        callback_url="https://yoursite.com/callback",
        payer_reference=data["payer_ref"],
        amount=data["amount"]
    )
    return jsonify({
        "payment_id": payment.payment_id,
        "bkash_url": payment.bkash_url
    })

if __name__ == "__main__":
    try:
        app.run()
    finally:
        client.close()
```
