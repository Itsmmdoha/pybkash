# pybkash

A Pythonic client for the bKash payment gateway. Supports both synchronous and asynchronous usage and covers the entire API surface.

## Features

1. Normal Payment
2. Agreement Creation
3. Agreement Payment
4. Refund
5. Search Transaction

## Installation

```bash
pip install pybkash
```

## Usage

### Synchronous Client

```python
from pybkash import Client, Token

# First, initialize the token. This will be passed to the Client.
token = Token(
    username="your_username",
    password="your_password", 
    app_key="your_app_key",
    app_secret="your_app_secret",
    sandbox=True  # Use False for production
)
```

Then, create a client object by passing the token:

```python
client = Client(token)
```

You can now use this client to perform various operations.

#### Step 1: Create Payment

```python
payment = client.create_payment(
    callback_url="https://yoursite.com/callback",
    payer_reference="CUSTOMER001",  # Passing a phone or bKash number pre-populates the wallet number field on the bKash checkout page.
    amount=1000  # Amount in BDT
)
```

This returns a `PaymentCreation` object:

* `payment.payment_id` is the ID bKash uses to identify individual payments.
* `payment.bkash_url` is the payment URL — send the user to this page.

After the user has completed the payment:

#### Step 2: Execute Payment

```python
execution = client.execute_payment(payment.payment_id)
```

This returns a `PaymentExecution` object.

```python
# Verify completion
if execution.is_complete():
    print(f"Payment successful! TrxID: {execution.trx_id}")
else:
    print(f"Payment status: {execution.status}")
```

## Documentation

For detailed synchronous and asynchronous usage information, including return types and attributes, see [docs](https://github.com/Itsmmdoha/pybkash/tree/main/docs).

