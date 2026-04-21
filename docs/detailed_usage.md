## Understanding the Flow

The bKash API follows a **3-step process** for agreements and payments:

1. **Create** - Initiates the transaction and returns a `bkash_url` for user authentication
2. **Execute** - Confirms the transaction after user completes authentication (for payments, money is deducted here)
3. **Query** - Queries transaction details, in case of need in future.


**Mental model:**
For **Agreements** and **Payments**: `Create → Execute → Query`

For **Refunds**: refunds are **executed directly** (there is no create step) and funds are returned immediately when the refund execution succeeds.

**Operational rules:**

* Always check the `status` field returned by execution, query, refund, and search responses.
* Use `is_complete()` on execution/query/refund objects to determine whether a transaction reached a successful terminal state.
* The `bkash_url` returned during creation **must** be used to redirect the user to the bKash authorization page.
* Agreement-based payments require **PIN only** (no OTP), enabling faster repeat checkouts.
* Passing the `agreement_id` parameter in the `create_payment()` method turns it into an agreement payment.
* You can get an `agreement_id` by creating an agreement with a customer.


## Table of Contents

- [Synchronous Client](#synchronous-client)
  - [Initialization](#initialization)
  - [Payment Methods](#payment-methods)
    - [1. Create Payment](#1-create-payment)
    - [2. Execute Payment](#2-execute-payment)
    - [3. Query Payment](#3-query-payment)
  - [Agreement Methods](#agreement-methods)
    - [4. Create Agreement](#4-create-agreement)
    - [5. Execute Agreement](#5-execute-agreement)
    - [6. Query Agreement](#6-query-agreement)
    - [7. Cancel Agreement](#7-cancel-agreement)
  - [Refund Methods](#refund-methods)
    - [8. Execute Refund](#8-execute-refund)
  - [Transaction Search Methods](#transaction-search-methods)
    - [9. Search Transaction](#9-search-transaction)
  - [Client Management](#client-management)
    - [10. Close Client](#10-close-client)
  - [Complete Payment Workflow Example](#complete-payment-workflow-example)
  - [Complete Agreement Payment Workflow Example](#complete-agreement-payment-workflow-example)
  - [Callback URL Redirection Query Parameters](#callback-url-redirection-query-parameters)
- [Asynchronous Client](#asynchronous-client)
  - [Initialization](#initialization-1)
  - [Using Async Methods](#using-async-methods)
  - [Complete Async Payment Example](#complete-async-payment-example)
  - [Using with Web Frameworks](#using-with-web-frameworks)


## Synchronous Client

### Initialization

First, initialize the token and client:

```python
from pybkash import Client, Token

# Initialize token with your credentials
token = Token(
    username="your_username",
    password="your_password", 
    app_key="your_app_key",
    app_secret="your_app_secret",
    sandbox=True, # Optional, default is False for production
    timeout=10    # Optional, default timeout is 10s
)

# Create client instance
client = Client(
    token,
    timeout=10    # Optional, default timeout is 10s
)
```

### Payment Methods

#### 1. Create Payment

Creates a new bKash payment transaction.

```python
payment = client.create_payment(
    callback_url="https://yoursite.com/callback",
    payer_reference="CUSTOMER001", # If the customer's wallet number is passed here, then it will be pre-populated in bKash's wallet number entry page.
    amount=1000,
    agreement_id=None,  # Optional, but passing an agreement_id here turns the payment into an Agreement Payment (no OTP)
    invoice_number=None,  # Optional
    merchant_association_info=None  # Optional
)

# Redirect user to payment.bkash_url
```

**Parameters:**
- `callback_url` (str, required): URL where bKash redirects after authentication
- `payer_reference` (str, required): Unique reference for the payer (phone/bKash number pre-populates checkout). Max length is 255 characters. Special characters "<", ">" and "&" are not allowed.
- `amount` (int, required): Payment amount in BDT
- `agreement_id` (str, optional): Agreement ID for tokenized payment (enables PIN-only flow)
- `invoice_number` (str, optional): Merchant invoice number
- `merchant_association_info` (str, optional): Merchant association information

**Returns:** `PaymentCreation` object with:

**Key Attributes:**
- `payment_id`: Payment identifier (required for execution)
- `bkash_url`: URL to redirect user for authentication

**Additional Attributes:**
- `status_code`: Response status code
- `status_message`: Response status message
- `callback_url`: Your callback URL
- `success_callback`: Success callback URL
- `failure_callback`: Failure callback URL
- `cancel_callback`: Cancel callback URL

#### 2. Execute Payment

Executes a payment after user completes authentication. **Money is deducted at this step.**

```python
execution = client.execute_payment(payment.payment_id)

if execution.is_complete():
    print(f"Payment successful! TrxID: {execution.trx_id}")
```

**Parameters:**
- `payment_id` (str, required): Payment ID from `create_payment()`

**Returns:** `PaymentExecution` object with:

**Key Attributes:**
- `status`: Transaction status (same as `transaction_status`)
- `transaction_status`: Transaction execution status
- `is_complete()`: Returns `True` if status is "Completed"
- `trx_id`: Transaction ID (save this for refunds/searches)

**Additional Attributes:**
- `payment_id`: Payment identifier
- `amount`: Payment amount
- `currency`: Currency (BDT)
- `customer_msisdn`: Customer phone number
- `payer_reference`: Payer reference
- `payment_execute_time`: Execution timestamp
- `merchant_invoice_number`: Invoice number
- `agreement_id`: Agreement ID (if agreement-based payment)
- `status_code`: Response status code
- `status_message`: Response status message
- `intent`: Payment intent

#### 3. Query Payment

Retrieves payment details and verifies status.

```python
query = client.query_payment(payment.payment_id)

if query.is_complete():
    print(f"Payment verified: {query.transaction_status}")
```

**Parameters:**
- `payment_id` (str, required): Payment ID from `create_payment()`

**Returns:** `Payment` object with:

**Key Attributes:**
- `status`: Payment status (same as `transaction_status`)
- `transaction_status`: Payment transaction status
- `is_complete()`: Returns `True` if status is "Completed"
- `verification_status`: Payment verification status

**Additional Attributes:**
- `payment_id`: Payment identifier
- `amount`: Payment amount
- `currency`: Currency (BDT)
- `payer_reference`: Payer reference
- `mode`: Payment mode
- `payment_create_time`: Creation timestamp
- `merchant_invoice`: Invoice number
- `intent`: Payment intent
- `agreement_id`: Agreement ID (if applicable)
- `agreement_status`: Agreement status (if applicable)
- `agreement_create_time`: Agreement creation time (if applicable)
- `agreement_execute_time`: Agreement execution time (if applicable)
- `status_code`: Response status code
- `status_message`: Response status message

### Agreement Methods

#### 4. Create Agreement

Creates a new bKash agreement for tokenized payments.

```python
agreement = client.create_agreement(
    callback_url="https://yoursite.com/callback",
    payer_reference="CUSTOMER001" # If the customer's wallet number is passed here, then it will be pre-populated in bKash's wallet number entry page.
)

# Redirect user to agreement.bkash_url
```

**Parameters:**
- `callback_url` (str, required): URL where bKash redirects after authentication
- `payer_reference` (str, required): Unique reference for the payer (phone/bKash number pre-populates checkout). Max length is 255 characters. Special characters "<", ">" and "&" are not allowed.

**Returns:** `AgreementCreation` object with:

**Key Attributes:**
- `payment_id`: Payment identifier (required for execution)
- `bkash_url`: URL to redirect user for authentication
- `agreement_status`: Agreement creation status

**Additional Attributes:**
- `agreement_create_time`: Creation timestamp
- `payer_reference`: Payer reference
- `callback_url`: Your callback URL
- `success_callback`: Success callback URL
- `failure_callback`: Failure callback URL
- `cancel_callback`: Cancel callback URL
- `status_code`: Response status code
- `status_message`: Response status message

#### 5. Execute Agreement

Executes an agreement after user authentication.

```python
agreement_execution = client.execute_agreement(agreement.payment_id)

if agreement_execution.is_complete():
    agreement_id = agreement_execution.agreement_id
```

**Parameters:**
- `payment_id` (str, required): Payment ID from `create_agreement()`

**Returns:** `AgreementExecution` object with:

**Key Attributes:**
- `status`: Agreement execution status (same as `agreement_status`)
- `agreement_status`: Agreement execution status
- `is_complete()`: Returns `True` if status is "Completed"
- `agreement_id`: Agreement identifier (save this for future payments!)

**Additional Attributes:**
- `payment_id`: Payment identifier
- `customer_msisdn`: Customer phone number
- `payer_reference`: Payer reference
- `agreement_execute_time`: Execution timestamp
- `status_code`: Response status code
- `status_message`: Response status message

#### 6. Query Agreement

Queries the status and details of an agreement.

```python
agreement_details = client.query_agreement(agreement.payment_id)

if agreement_details.is_complete():
    print(f"Agreement active: {agreement_details.agreement_status}")
```

**Parameters:**
- `payment_id` (str, required): Payment ID from `create_agreement()`

**Returns:** `Agreement` object with:

**Key Attributes:**
- `status`: Agreement status (same as `agreement_status`)
- `agreement_status`: Agreement query status
- `is_complete()`: Returns `True` if status is "Completed"
- `agreement_id`: Agreement identifier

**Additional Attributes:**
- `payment_id`: Payment identifier
- `payer_reference`: Payer reference
- `payer_account`: Payer account number
- `payer_type`: Payer type
- `agreement_create_time`: Creation timestamp
- `agreement_execute_time`: Execution timestamp
- `mode`: Agreement mode
- `verification_status`: Verification status
- `status_code`: Response status code
- `status_message`: Response status message

#### 7. Cancel Agreement

Cancels an existing agreement.

```python
cancellation = client.cancel_agreement(agreement_id="AGR123456")

if cancellation.is_complete():
    print(f"Cancelled at: {cancellation.agreement_void_time}")
```

**Parameters:**
- `agreement_id` (str, required): The agreement ID to cancel

**Returns:** `AgreementCancellation` object with:

**Key Attributes:**
- `status`: Cancellation status ("Completed" if `agreement_status` is "Cancelled")
- `agreement_status`: Agreement status after cancellation
- `is_complete()`: Returns `True` if cancellation succeeded

**Additional Attributes:**
- `payment_id`: Payment identifier
- `agreement_id`: Agreement identifier
- `payer_reference`: Payer reference
- `agreement_void_time`: Cancellation timestamp
- `status_code`: Response status code
- `status_message`: Response status message

### Refund Methods

#### 8. Execute Refund

Executes a refund for a completed payment. Funds are returned immediately when successful.

```python
refund = client.execute_refund(
    payment_id="TR0001H7QAn2Q1769586741067",
    trx_id="DAS60OCK6O",
    refund_amount=100,
    sku="PRODUCT123",  # Optional
    reason="Customer requested refund"  # Optional
)

if refund.is_complete():
    print(f"Refund successful: {refund.refund_trx_id}")
```

**Parameters:**
- `payment_id` (str, required): Payment ID from the original payment
- `trx_id` (str, required): Transaction ID from the original payment
- `refund_amount` (int, required): Amount to refund in BDT
- `sku` (str, optional): SKU/product identifier
- `reason` (str, optional): Reason for the refund

**Returns:** `RefundExecution` object with:

**Key Attributes:**
- `status`: Refund transaction status (same as `transaction_status`)
- `transaction_status`: Refund execution status
- `is_complete()`: Returns `True` if status is "Completed"
- `trx_id`: Refund transaction ID (same as `refund_trx_id`)
- `refund_trx_id`: Refund transaction ID

**Additional Attributes:**
- `original_trx_id`: Original transaction ID
- `amount`: Refunded amount
- `currency`: Currency (BDT)
- `completed_time`: Refund completion timestamp
- `status_code`: Response status code
- `status_message`: Response status message

### Transaction Search Methods

#### 9. Search Transaction

Searches for a transaction by transaction ID.

```python
transaction = client.search_trx(trx_id="DAS60OCK6O")

if transaction.is_complete():
    print(f"Transaction found: {transaction.transaction_status}")
```

**Parameters:**
- `trx_id` (str, required): The transaction ID to search for

**Returns:** `Transaction` object with:

**Key Attributes:**
- `status`: Transaction status (same as `transaction_status`)
- `transaction_status`: Transaction search status
- `is_complete()`: Returns `True` if status is "Completed"
- `trx_id`: Transaction ID

**Additional Attributes:**
- `transaction_type`: Transaction type
- `amount`: Transaction amount
- `currency`: Currency (BDT)
- `customer_msisdn`: Customer phone number
- `payer_account`: Payer account
- `initiation_time`: Transaction initiation timestamp
- `completed_time`: Transaction completion timestamp
- `organization_short_code`: Organization code
- `status_code`: Response status code
- `status_message`: Response status message
- `service_fee`: Service fee (not present in refund transactions)
- `payer_type`: Payer type (not present in refund transactions)
- `credited_amount`: Credited amount (not present in refund transactions)
- `max_refundable_amount`: Maximum refundable amount (not present in refund transactions)
- `original_trx_amount`: Original transaction amount (only for refund transactions)

### Client Management

#### 10. Close Client

Closes the HTTP client connection. Always call this when done using the client.

```python
client.close()
```

### Complete Payment Workflow Example

```python
from pybkash import Client, Token

token = Token(
    username="your_username",
    password="your_password",
    app_key="your_app_key",
    app_secret="your_app_secret",
    sandbox=True
)
client = Client(token)

try:
    # Step 1: Create payment
    payment = client.create_payment(
        callback_url="https://yoursite.com/callback",
        payer_reference="CUSTOMER001",
        amount=1000
    )
    # Redirect user to payment.bkash_url
    
    # User completes authentication on bKash page
    # bKash redirects to your callback with query parameters
    
    # Step 2: Execute payment (after callback receives status=success)
    execution = client.execute_payment(payment.payment_id)
    
    if execution.is_complete():
        print(f"Payment successful! TrxID: {execution.trx_id}")
        
finally:
    client.close()
```

### Complete Agreement Payment Workflow Example

```python
from pybkash import Client, Token

token = Token(
    username="your_username",
    password="your_password",
    app_key="your_app_key",
    app_secret="your_app_secret",
    sandbox=True
)
client = Client(token)

try:
    # Step 1: Create agreement
    agreement = client.create_agreement(
        callback_url="https://yoursite.com/callback",
        payer_reference="CUSTOMER001"
    )
    # Redirect user to agreement.bkash_url
    
    # Step 2: Execute agreement (after user authenticates)
    agreement_execution = client.execute_agreement(agreement.payment_id)
    
    if agreement_execution.is_complete():
        agreement_id = agreement_execution.agreement_id
        
        # Step 3: Use agreement for future payments (PIN-only, no OTP!)
        payment = client.create_payment(
            callback_url="https://yoursite.com/callback",
            payer_reference="CUSTOMER001",
            amount=500,
            agreement_id=agreement_id  # Pass agreement_id for agreement payment
        )
        
        payment_execution = client.execute_payment(payment.payment_id)
        
        if payment_execution.is_complete():
            print(f"Agreement payment successful! TrxID: {payment_execution.trx_id}")
        
finally:
    client.close()
```

### Callback URL Redirection Query Parameters

When creating a payment or agreement, you provide a **base `callback_url`**, for example:

```
https://yoursite.com/callback
```

After the user completes, fails, or cancels the transaction on the bKash page, bKash redirects the user back to this URL with **query parameters appended**.

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

These query parameters act as a **signal** indicating that the user has finished interacting with the bKash page.

At this point:

* Inspect the `status` parameter
* If `status=success`, **attempt to execute the payment/agreement** using the `paymentID` from the query parameters
* Money is only deducted when you execute the payment
* Always verify the final state by calling `is_complete()` on execution and query objects

> **Important:** The callback redirection alone should **not** be treated as final confirmation of a successful transaction, as users can manipulate it. Always execute and verify server-side.


## Asynchronous Client

The asynchronous client provides the same functionality as the synchronous client but uses `async/await` for non-blocking operations. This is ideal for web applications and services that handle multiple concurrent requests.

### Initialization

```python
import asyncio
from pybkash import AsyncClient, AsyncToken

async_token = AsyncToken(
    username="your_username",
    password="your_password",
    app_key="your_app_key",
    app_secret="your_app_secret",
    sandbox=True, # Optional, default is False for production
    timeout=10    # Optional, default timeout is 10s
)

client = AsyncClient(
    async_token,
    timeout=10    # Optional, default timeout is 10s
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

---

For more information about the bKash API, visit the [official bKash API documentation](https://developer.bka.sh/).
