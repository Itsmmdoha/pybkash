class CreationBase:
    def __init__(
        self,
        status_code: str | int,
        status_message: str,
        payment_id: str,
        bkash_url: str,
        callback_url: str,
        success_callback: str,
        failure_callback: str,
        cancel_callback: str,
    ) -> None:
        self.status_code = status_code
        self.status_message = status_message
        self.payment_id = payment_id
        self.bkash_url = bkash_url
        self.callback_url = callback_url
        self.success_callback = success_callback
        self.failure_callback = failure_callback
        self.cancel_callback = cancel_callback

class StatusMixin:
    status: str

    def is_complete(self) -> bool:
        return self.status.upper() == "COMPLETED"

class ExecutionBase(StatusMixin):
    def __init__(
        self,
        status_code: str,
        status_message: str,
        payment_id: str,
        agreement_id: str | None,
        payer_reference: str,
        customer_msisdn: str,
    ) -> None:
        self.status_code = status_code
        self.status_message = status_message
        self.payment_id = payment_id
        self.agreement_id = agreement_id
        self.payer_reference = payer_reference
        self.customer_msisdn = customer_msisdn

class QueryBase(StatusMixin):
    def __init__(
        self,
        status_code: str,
        status_message: str,
        payment_id: str,
        payer_reference: str,
        agreement_id: str | None = None,
        agreement_status: str | None = None,
        agreement_create_time: str | None = None,
        agreement_execute_time: str | None = None,
        verification_status: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.status_message = status_message
        self.payment_id = payment_id
        self.payer_reference = payer_reference
        self.agreement_id = agreement_id
        self.agreement_status = agreement_status
        self.agreement_create_time = agreement_create_time
        self.agreement_execute_time = agreement_execute_time
        self.verification_status = verification_status

class PaymentCreation(CreationBase):
    def __init__(
        self,
        status_code: int,
        status_message: str,
        payment_id: str,
        bkash_url: str,
        callback_url: str,
        success_callback: str,
        failure_callback: str,
        cancel_callback: str,
    ) -> None:
        super().__init__(
            status_code=status_code,
            status_message=status_message,
            payment_id=payment_id,
            bkash_url=bkash_url,
            callback_url=callback_url,
            success_callback=success_callback,
            failure_callback=failure_callback,
            cancel_callback=cancel_callback,
        )

class AgreementCreation(CreationBase):
    def __init__(
        self,
        status_code: str,
        status_message: str,
        payment_id: str,
        bkash_url: str,
        callback_url: str,
        success_callback: str,
        failure_callback: str,
        cancel_callback: str,
        payer_reference: str,
        agreement_status: str,
        agreement_create_time: str,
    ) -> None:
        super().__init__(
            status_code=status_code,
            status_message=status_message,
            payment_id=payment_id,
            bkash_url=bkash_url,
            callback_url=callback_url,
            success_callback=success_callback,
            failure_callback=failure_callback,
            cancel_callback=cancel_callback,
        )

        self.payer_reference = payer_reference
        self.agreement_status = agreement_status
        self.agreement_create_time = agreement_create_time

class RefundExecution(StatusMixin):
    def __init__(
        self,
        original_trx_id: str,
        refund_trx_id: str,
        transaction_status: str,
        amount: str,
        currency: str,
        completed_time: str,
        status_code: str,
        status_message: str,
    ) -> None:
        self.status = transaction_status # universal status
        self.trx_id = refund_trx_id # universal trx_id
        self.original_trx_id = original_trx_id
        self.refund_trx_id = refund_trx_id
        self.transaction_status = transaction_status
        self.amount = amount
        self.currency = currency
        self.completed_time = completed_time
        self.status_code = status_code
        self.status_message = status_message


class AgreementExecution(ExecutionBase):
    def __init__(
        self,
        status_code: str,
        status_message: str,
        payment_id: str,
        agreement_id: str,
        payer_reference: str,
        customer_msisdn: str,
        agreement_execute_time: str,
        agreement_status: str,
    ) -> None:
        super().__init__(
            status_code=status_code,
            status_message=status_message,
            payment_id=payment_id,
            agreement_id=agreement_id,
            payer_reference=payer_reference,
            customer_msisdn=customer_msisdn,
        )

        self.status = agreement_status  # universal status
        self.agreement_status = agreement_status
        self.agreement_execute_time = agreement_execute_time

class PaymentExecution(ExecutionBase):
    def __init__(
        self,
        status_code: str,
        status_message: str,
        payment_id: str,
        agreement_id: str | None,
        payer_reference: str,
        customer_msisdn: str,
        trx_id: str,
        amount: str,
        transaction_status: str,
        payment_execute_time: str,
        currency: str,
        intent: str,
        merchant_invoice_number: str,
    ) -> None:
        super().__init__(
            status_code=status_code,
            status_message=status_message,
            payment_id=payment_id,
            agreement_id=agreement_id,
            payer_reference=payer_reference,
            customer_msisdn=customer_msisdn,
        )

        self.status = transaction_status  # universal status
        self.trx_id = trx_id
        self.transaction_status = transaction_status
        self.amount = amount
        self.payment_execute_time = payment_execute_time
        self.currency = currency
        self.intent = intent
        self.merchant_invoice_number = merchant_invoice_number

class Agreement(QueryBase):
    def __init__(
        self,
        status_code: str,
        status_message: str,
        payment_id: str,
        agreement_id: str,
        payer_reference: str,
        payer_account: str,
        payer_type: str,
        agreement_status: str,
        agreement_create_time: str,
        agreement_execute_time: str,
        mode: str,
        verification_status: str,
    ) -> None:
        super().__init__(
            status_code=status_code,
            status_message=status_message,
            payment_id=payment_id,
            payer_reference=payer_reference,
            agreement_id=agreement_id,
            agreement_status=agreement_status,
            agreement_create_time=agreement_create_time,
            agreement_execute_time=agreement_execute_time,
            verification_status=verification_status,
        )
        self.status = agreement_status
        self.payer_account = payer_account
        self.payer_type = payer_type
        self.mode = mode

class Payment(QueryBase):
    def __init__(
        self,
        status_code: str,
        status_message: str,
        payment_id: str,
        payer_reference: str,
        mode: str,
        payment_create_time: str,
        amount: str,
        currency: str,
        intent: str,
        merchant_invoice: str,
        transaction_status: str,
        verification_status: str,
        agreement_id: str | None,
        agreement_status: str | None,
        agreement_create_time: str | None,
        agreement_execute_time: str | None,
    ) -> None:
        super().__init__(
            status_code=status_code,
            status_message=status_message,
            payment_id=payment_id,
            payer_reference=payer_reference,
            agreement_id=agreement_id,
            agreement_status=agreement_status,
            agreement_create_time=agreement_create_time,
            agreement_execute_time=agreement_execute_time,
            verification_status=verification_status,
        )

        self.status = transaction_status
        self.transaction_status = transaction_status
        self.mode = mode
        self.payment_create_time = payment_create_time
        self.amount = amount
        self.currency = currency
        self.intent = intent
        self.merchant_invoice = merchant_invoice

class Transaction(StatusMixin):
    def __init__(
        self,
        trx_id: str,
        initiation_time: str,
        completed_time: str,
        transaction_type: str,
        customer_msisdn: str,
        payer_account: str,
        transaction_status: str,
        amount: str,
        currency: str,
        organization_short_code: str,
        status_code: str,
        status_message: str,

        # following 4 not present in refund transactions
        service_fee: str | None = None,
        payer_type: str | None = None,
        credited_amount: str | None = None,
        max_refundable_amount: str | None = None,

        # this key is only sent for the refund transcations
        original_trx_amount: str | None = None,
    ) -> None:
        self.status = transaction_status
        self.trx_id = trx_id
        self.initiation_time = initiation_time
        self.completed_time = completed_time
        self.transaction_type = transaction_type
        self.customer_msisdn = customer_msisdn
        self.payer_account = payer_account
        self.transaction_status = transaction_status
        self.amount = amount
        self.currency = currency
        self.organization_short_code = organization_short_code
        self.status_code = status_code
        self.status_message = status_message

        self.service_fee = service_fee
        self.payer_type = payer_type
        self.credited_amount = credited_amount
        self.max_refundable_amount = max_refundable_amount

        self.original_trx_amount = original_trx_amount

class AgreementCancellation(StatusMixin):
    def __init__(
        self,
        status_code: str,
        status_message: str,
        payment_id: str,
        agreement_id: str,
        payer_reference: str,
        agreement_void_time: str,
        agreement_status: str,
    ) -> None:
        # this is status of the cancellation not the agreement
        self.status = "Complete" if agreement_status == "Cancelled" else agreement_status # universal status
        # this is to make StatusMixin is_complete() method work intuitively
        # the method returns True on status = 'Complete'
        self.status_code = status_code
        self.status_message = status_message
        self.payment_id = payment_id
        self.agreement_id = agreement_id
        self.payer_reference = payer_reference
        self.agreement_void_time = agreement_void_time
        self.agreement_status = agreement_status


