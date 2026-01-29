# API Documentation

This document provides detailed information about return types and their attributes in the pybkash package.

For more information about the bKash API itself, visit the [official bKash API documentation](https://developer.bka.sh/).

## Return Types

### PaymentCreation

Returned by `create_payment()` method.

**Attributes:**
- `status_code` (int): Response status code
- `status_message` (str): Response status message
- `payment_id` (str): Unique payment identifier - use this for execute and query
- `bkash_url` (str): URL to redirect user for authentication
- `callback_url` (str): Your callback URL
- `success_callback` (str): Success callback URL
- `failure_callback` (str): Failure callback URL
- `cancel_callback` (str): Cancel callback URL

### AgreementCreation

Returned by `create_agreement()` method.

**Attributes:**
- `status_code` (str): Response status code
- `status_message` (str): Response status message
- `payment_id` (str): Unique payment identifier - use this for execute and query
- `bkash_url` (str): URL to redirect user for authentication
- `callback_url` (str): Your callback URL
- `success_callback` (str): Success callback URL
- `failure_callback` (str): Failure callback URL
- `cancel_callback` (str): Cancel callback URL
- `payer_reference` (str): Payer reference
- `agreement_status` (str): Agreement status
- `agreement_create_time` (str): Agreement creation timestamp

### PaymentExecution

Returned by `execute_payment()` method. Includes `is_complete()` method.

**Attributes:**
- `status_code` (str): Response status code
- `status_message` (str): Response status message
- `payment_id` (str): Payment identifier
- `payer_reference` (str): Payer reference
- `customer_msisdn` (str): Customer's mobile number
- `trx_id` (str): Transaction ID - use this for refunds and transaction search
- `amount` (str): Payment amount
- `transaction_status` (str): Transaction status (same as `status`)
- `status` (str): Universal status field - use with `is_complete()`
- `payment_execute_time` (str): Payment execution timestamp
- `currency` (str): Currency code (BDT)
- `intent` (str): Payment intent
- `merchant_invoice_number` (str): Merchant invoice number
- `agreement_id` (str | None): Agreement ID if payment was made using an agreement

**Methods:**
- `is_complete()` -> bool: Returns True if transaction status is "COMPLETED"

### AgreementExecution

Returned by `execute_agreement()` method. Includes `is_complete()` method.

**Attributes:**
- `status_code` (str): Response status code
- `status_message` (str): Response status message
- `payment_id` (str): Payment identifier
- `agreement_id` (str): Agreement ID - save this for future tokenized payments
- `payer_reference` (str): Payer reference
- `customer_msisdn` (str): Customer's mobile number
- `agreement_execute_time` (str): Agreement execution timestamp
- `agreement_status` (str): Agreement status (same as `status`)
- `status` (str): Universal status field - use with `is_complete()`

**Methods:**
- `is_complete()` -> bool: Returns True if agreement status is "COMPLETED"

### Payment

Returned by `query_payment()` method. Includes `is_complete()` method.

**Attributes:**
- `status_code` (str): Response status code
- `status_message` (str): Response status message
- `payment_id` (str): Payment identifier
- `payer_reference` (str): Payer reference
- `mode` (str): Payment mode
- `payment_create_time` (str): Payment creation timestamp
- `amount` (str): Payment amount
- `currency` (str): Currency code
- `intent` (str): Payment intent
- `merchant_invoice` (str): Merchant invoice number
- `transaction_status` (str): Transaction status (same as `status`)
- `status` (str): Universal status field - use with `is_complete()`
- `verification_status` (str): Verification status
- `agreement_id` (str | None): Agreement ID if applicable
- `agreement_status` (str | None): Agreement status if applicable
- `agreement_create_time` (str | None): Agreement creation time if applicable
- `agreement_execute_time` (str | None): Agreement execution time if applicable

**Methods:**
- `is_complete()` -> bool: Returns True if transaction status is "COMPLETED"

### Agreement

Returned by `query_agreement()` method. Includes `is_complete()` method.

**Attributes:**

* `status_code` (str): Response status code
* `status_message` (str): Response status message
* `payment_id` (str): Payment identifier
* `agreement_id` (str): Agreement ID
* `payer_reference` (str): Payer reference
* `payer_account` (str): Payer's account or mobile number
* `payer_type` (str): Type of the payer
* `mode` (str): Transaction mode
* `agreement_status` (str): Current status of the agreement
* `status` (str): Universal status field - use with `is_complete()`
* `verification_status` (str): Verification status of the agreement
* `agreement_create_time` (str): Agreement creation timestamp
* `agreement_execute_time` (str): Agreement execution timestamp

**Methods:**
- `is_complete()` -> bool: Returns True if agreement status is "COMPLETED"

### RefundExecution

Returned by `execute_refund()` method. Includes `is_complete()` method.

**Attributes:**
- `original_trx_id` (str): Original transaction ID
- `refund_trx_id` (str): Refund transaction ID (same as `trx_id`)
- `trx_id` (str): Universal transaction ID field
- `transaction_status` (str): Transaction status (same as `status`)
- `status` (str): Universal status field - use with `is_complete()`
- `amount` (str): Refund amount
- `currency` (str): Currency code
- `completed_time` (str): Refund completion timestamp
- `status_code` (str): Response status code
- `status_message` (str): Response status message

**Methods:**
- `is_complete()` -> bool: Returns True if refund status is "COMPLETED"

### Transaction

Returned by `search_trx()` method. Includes `is_complete()` method.

**Attributes:**
- `trx_id` (str): Transaction ID
- `initiation_time` (str): Transaction initiation timestamp
- `completed_time` (str): Transaction completion timestamp
- `transaction_type` (str): Type of transaction
- `customer_msisdn` (str): Customer's mobile number
- `payer_account` (str): Payer account
- `transaction_status` (str): Transaction status (same as `status`)
- `status` (str): Universal status field - use with `is_complete()`
- `amount` (str): Transaction amount
- `currency` (str): Currency code
- `organization_short_code` (str): Organization short code
- `status_code` (str): Response status code
- `status_message` (str): Response status message
- `service_fee` (str | None): Service fee (not present in refund transactions)
- `payer_type` (str | None): Payer type (not present in refund transactions)
- `credited_amount` (str | None): Credited amount (not present in refund transactions)
- `max_refundable_amount` (str | None): Maximum refundable amount (not present in refund transactions)
- `original_trx_amount` (str | None): Original transaction amount (only present in refund transactions)

**Methods:**
- `is_complete()` -> bool: Returns True if transaction status is "COMPLETED"

## Common Patterns

### Checking Status

All execution, query, refund, and transaction objects have a `status` attribute and `is_complete()` method:

```python
# Using is_complete()
if execution.is_complete():
    print("Transaction successful!")

# Using status directly
if execution.status == "COMPLETED":
    print("Transaction successful!")
```

### Getting Transaction IDs

Transaction IDs are essential for refunds and searches:

```python
# From payment execution
execution = client.execute_payment(payment_id)
trx_id = execution.trx_id

# Use for refund
refund = client.execute_refund(
    payment_id=payment_id,
    trx_id=trx_id,
    refund_amount=500
)

# Use for search
transaction = client.search_trx(trx_id)
```

### Using Agreement IDs

Save agreement IDs from agreement execution for future payments:

```python
# Execute agreement
agreement_exec = client.execute_agreement(payment_id)
agreement_id = agreement_exec.agreement_id  # Save this!

# Use in future payments
payment = client.create_payment(
    callback_url="...",
    payer_reference="...",
    amount=1000,
    agreement_id=agreement_id  # Enables PIN-only flow
)
```

## Status Values

Common status values you may encounter:

- `"Complete"` - Transaction successful
- `"Initiated"` - Transaction initiated
- `"InProgress"` - Transaction in progress
- `"Cancelled"` - Transaction cancelled by user
- `"Failed"` - Transaction failed

**Note:** Always use the `is_complete()` method or check for a status to be "Complete".
