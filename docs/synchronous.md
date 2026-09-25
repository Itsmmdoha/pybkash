## Synchronous Client

### Initialization

First, initialize the token and client. See [Token Caching](token-caching.md) for in-memory vs Redis cache.

```python
from pybkash import Client, Token

# Initialize token with your credentials
token = Token(
    username="your_username",
    password="your_password", 
    app_key="your_app_key",
    app_secret="your_app_secret",
    sandbox=True  # Optional, default is False for production
)

# Create client instance
client = Client(
    token,
    timeout=10,  # Optional, default timeout is 10s
    max_connections=50,  # Optional, max concurrent connections. Defaults to 50.
    max_keepalive_connections=20,  # Optional, max idle connections to keep. Defaults to 20.
    keepalive_expiry=20.0  # Optional, idle connection expiry time in seconds. Defaults to 20.0.
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
- `amount` (float, required): Payment amount in BDT. At least 1, up to 2 decimal places; otherwise raises `ValueError`.
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
- `refund_amount` (float, required): Amount to refund in BDT. At least 1, up to 2 decimal places; otherwise raises `ValueError`.
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
