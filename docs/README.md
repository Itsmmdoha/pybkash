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

- [Token Caching](token-caching.md)
- [Synchronous Client](synchronous.md)
  - [Initialization](synchronous.md#initialization)
  - [Payment Methods](synchronous.md#payment-methods)
    - [1. Create Payment](synchronous.md#1-create-payment)
    - [2. Execute Payment](synchronous.md#2-execute-payment)
    - [3. Query Payment](synchronous.md#3-query-payment)
  - [Agreement Methods](synchronous.md#agreement-methods)
    - [4. Create Agreement](synchronous.md#4-create-agreement)
    - [5. Execute Agreement](synchronous.md#5-execute-agreement)
    - [6. Query Agreement](synchronous.md#6-query-agreement)
    - [7. Cancel Agreement](synchronous.md#7-cancel-agreement)
  - [Refund Methods](synchronous.md#refund-methods)
    - [8. Execute Refund](synchronous.md#8-execute-refund)
  - [Transaction Search Methods](synchronous.md#transaction-search-methods)
    - [9. Search Transaction](synchronous.md#9-search-transaction)
  - [Client Management](synchronous.md#client-management)
    - [10. Close Client](synchronous.md#10-close-client)
  - [Complete Payment Workflow Example](synchronous.md#complete-payment-workflow-example)
  - [Complete Agreement Payment Workflow Example](synchronous.md#complete-agreement-payment-workflow-example)
  - [Callback URL Redirection Query Parameters](synchronous.md#callback-url-redirection-query-parameters)
- [Asynchronous Client](asynchronous.md)
  - [Initialization](asynchronous.md#initialization)
  - [Using Async Methods](asynchronous.md#using-async-methods)
  - [Complete Async Payment Example](asynchronous.md#complete-async-payment-example)
  - [Using with Web Frameworks](asynchronous.md#using-with-web-frameworks)
- [Context Managers](context-managers.md)
  - [Synchronous](context-managers.md#synchronous)
  - [Asynchronous](context-managers.md#asynchronous)


For more information about the bKash API, visit the [official bKash API documentation](https://developer.bka.sh/).
