## Understanding the Flow

The bKash API follows a **3-step process** for agreements and payments:

1. **Create** - Initiates the transaction and returns a `bkash_url` for user authentication
2. **Execute** - Confirms the transaction after user completes authentication (for payments, money is deducted here)
3. **Query** - Retrieves transaction details and verifies the `status`


**Mental model:**
For **Agreements** and **Payments**: `Create → Execute → Query`

For **Refunds**: refunds are **executed directly** (there is no create step) and funds are returned immediately when the refund execution succeeds.

**Operational rules:**

* Always check the `status` field returned by execution, query, refund, and search responses.
* Use `is_complete()` on execution/query/refund objects to determine whether a transaction reached a successful terminal state.
* The `bkash_url` returned during creation **must** be used to redirect the user to the bKash authorization page.
* Agreement-based payments require **PIN only** (no OTP), enabling faster repeat checkouts.



**Key concepts:**
- Always check the `status` attribute on execution, query and refund responses
- Use the `is_complete()` method to verify if a transaction succeeded
- The `bkash_url` from creation objects is where you need to send users for the payment/agreement (bKash payment/agreement page)
- Agreement payments require only PIN (no OTP) for faster checkout 

## Usage

### Synchronous Client

```python
from pybkash import Client, Token

# You first initialize token and client, this will be passed to the Clients
token = Token(
    username="your_username",
    password="your_password", 
    app_key="your_app_key",
    app_secret="your_app_secret",
    sandbox=True  # Use False for production
)
```
Then pass this token to the client to create client objects,

```python
client = Client(token)

```
You can now use this client to perform various operations,

Step 1: Create payment,
```python
payment = client.create_payment(
    callback_url="https://yoursite.com/callback",
    payer_reference="CUSTOMER001", # A phone or bKash number here will pre-populate the wallet number field on the bKash checkout page.
    amount=1000  # Amount in BDT
)
# Send user to: payment.bkash_url
# When the payment is complete/cancelled/failed bkash redirects the user to 
# your callback_url with query parameters, and using those params you'll know when and if you should execute a Payment/Agreement
# More on this callback redirection query parameters later
```

Step 2: Execute payment (after user authenticates)
```python
execution = client.execute_payment(payment.payment_id)

# Verify completion
if execution.is_complete():
    print(f"Payment successful! TrxID: {execution.trx_id}")
else:
    print(f"Payment status: {execution.status}")
```

Step 3: Query payment details (optional, for future reference)
```python
query = client.query_payment(payment.payment_id)
print(f"Transaction status: {query.status}")
```
```python
# Close client (closes any open connections)
client.close()
```


### Callback URL Redirection Query Parameters

When creating a payment, you provide a **base `callback_url`**, for example:

```
https://yoursite.com/callback
```

After the user completes, fails, or cancels the payment on the bKash page, bKash redirects the user back to this URL with **query parameters appended**.

Example redirections:

```
https://yoursite.com/callback?version=v1.2.0-beta&product=tokenized-checkout&paymentID=TR0011dQPHnuY1720518383420&status=success&signature=cm8HBfl65A
```

```
https://yoursite.com/callback?version=v1.2.0-beta&product=tokenized-checkout&paymentID=TR0011dQPHnuY1720518383420&status=failure&signature=cm8HBfl65A
```

```
https://yoursite.com/callback?version=v1.2.0-beta&product=tokenized-checkout&paymentID=TR0011dQPHnuY1720518383420&status=cancel&signature=cm8HBfl65A
```

These query parameters act as a **signal (or clue)** indicating that the user has finished interacting with the bKash page.

At this point:

* You should inspect the `status` parameter
* If `status=success`, **attempt to execute the payment** using the payment_id from the query parameters
* It's only when you execute the payment will the money be deducted from the user and taken to merchant's account
* Always verify the final state yourself by calling the `is_complete()`  on execution and query objects.

> Note: The callback redirection alone should **not** be treated as final confirmation of a successful payment as the users can manipulate it.


### Agreement Payments

```python
# Step 1: Create agreement
agreement = client.create_agreement(
    callback_url="https://yoursite.com/callback",
    payer_reference="CUSTOMER001"
)
# Send user to: agreement.bkash_url

# Step 2: Execute agreement (after user authenticates)
agreement_execution = client.execute_agreement(agreement.payment_id)
agreement_id = agreement_execution.agreement_id  # Save this!

# Step 3: Use agreement for future payments (PIN-only, no OTP)
payment = client.create_payment(
    callback_url="https://yoursite.com/callback",
    payer_reference="CUSTOMER001",
    amount=500,
    agreement_id=agreement_id  # Passing the agreement_id here enables Agreement Payment
)
# Proceed with execute/query as normal

```

#### Refunds

Refunds are executed directly against a completed payment:

```python
refund = client.execute_refund(
    payment_id="TR0001H7QAn2Q1769586741067",
    trx_id="DAS60OCK6O",
    refund_amount=100,  # Amount in BDT
)

if refund.is_complete():
    print(f"Refund successful! Refund TrxID: {refund.trx_id}")
    print(f"Original TrxID: {refund.original_trx_id}")
else:
    print(f"Refund status: {refund.status}")
```

#### Search Transaction

```python
transaction = client.search_trx(trx_id="DAS60OCK6O")
print(transaction.status)
print(transaction.amount)
```


### Asynchronous Client

The asynchronous client API mirrors the synchronous API. All create, execute, query, refund and search operations **must be awaited**.


```python
import asyncio
from pybkash import AsyncClient, AsyncToken

async_token = AsyncToken(
    username="your_username",
    password="your_password",
    app_key="your_app_key",
    app_secret="your_app_secret",
    sandbox=True
)

client = AsyncClient(async_token)
```

#### Async payment flow

```python
async def process_payment():
    # Step 1: Create payment (await required)
    payment = await client.create_payment(
        callback_url="https://yoursite.com/callback",
        payer_reference="CUSTOMER001",
        amount=1000
    )
    # Redirect user to: payment.bkash_url

    # Step 2: Execute payment (await required)
    execution = await client.execute_payment(payment.payment_id)

    if execution.is_complete():
        print(f"Payment successful! TrxID: {execution.trx_id}")
    else:
        print(f"Payment status: {execution.status}")

    # Step 3: Query payment (await required)
    query = await client.query_payment(payment.payment_id)
    print(f"Transaction status: {query.status}")

    await client.aclose()

asyncio.run(process_payment())
```


For more information about the bKash API, visit the [official bKash API documentation](https://developer.bka.sh/).
