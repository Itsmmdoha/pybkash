from httpx import Client as SyncClient, AsyncClient as HttpxAsyncClient, Response
from .token_manager import Token, AsyncToken
from .exception_handlers import raise_api_exception
from .models import ( 
    PaymentCreation,
    AgreementCreation, 
    PaymentExecution, 
    AgreementExecution, 
    RefundExecution, 
    Agreement, 
    Payment,
    Transaction,
    AgreementCancellation
)


class BaseClient:
    def _create_agreement_object(self, response: dict) -> AgreementCreation:
        return AgreementCreation(
            status_code=response["statusCode"],
            status_message=response["statusMessage"],
            payment_id=response["paymentID"],
            bkash_url=response["bkashURL"],
            callback_url=response["callbackURL"],
            success_callback=response["successCallbackURL"],
            failure_callback=response["failureCallbackURL"],
            cancel_callback=response["cancelledCallbackURL"],
            payer_reference=response["payerReference"],
            agreement_status=response["agreementStatus"],
            agreement_create_time=response["agreementCreateTime"],
        )

    def _create_payment_object(self, payment_response: dict) -> PaymentCreation:
        payment = PaymentCreation(
            status_code=payment_response["statusCode"],
            status_message=payment_response["statusMessage"],
            payment_id=payment_response["paymentID"],
            bkash_url=payment_response["bkashURL"],
            callback_url=payment_response["callbackURL"],
            success_callback=payment_response["successCallbackURL"],
            failure_callback=payment_response["failureCallbackURL"],
            cancel_callback=payment_response["cancelledCallbackURL"],
        )
        return payment



    def _create_payment_execution_object(self, response: dict) -> PaymentExecution:
        return PaymentExecution(
            status_code=response["statusCode"],
            status_message=response["statusMessage"],
            payment_id=response["paymentID"],
            payer_reference=response["payerReference"],
            customer_msisdn=response["customerMsisdn"],
            trx_id=response["trxID"],
            amount=response["amount"],
            transaction_status=response["transactionStatus"],
            payment_execute_time=response["paymentExecuteTime"],
            currency=response["currency"],
            intent=response["intent"],
            merchant_invoice_number=response["merchantInvoiceNumber"],
            agreement_id=response.get("agreementID"),
        )
    def _create_agreement_cancellation_object(self, response: dict,) -> AgreementCancellation:
        return AgreementCancellation(
            status_code=response["statusCode"],
            status_message=response["statusMessage"],
            payment_id=response["paymentID"],
            agreement_id=response["agreementID"],
            payer_reference=response["payerReference"],
            agreement_void_time=response["agreementVoidTime"],
            agreement_status=response["agreementStatus"],
        )


    def _create_agreement_execution_object(self, response: dict) -> AgreementExecution:
        return AgreementExecution(
            status_code=response["statusCode"],
            status_message=response["statusMessage"],
            payment_id=response["paymentID"],
            agreement_id=response["agreementID"],
            payer_reference=response["payerReference"],
            customer_msisdn=response["customerMsisdn"],
            agreement_execute_time=response["agreementExecuteTime"],
            agreement_status=response["agreementStatus"],
        )

    def _create_agreement_query_object(self, response: dict) -> Agreement:
        return Agreement(
            status_code=response["statusCode"],
            status_message=response["statusMessage"],
            payment_id=response["paymentID"],
            agreement_id=response["agreementID"],
            payer_reference=response["payerReference"],
            payer_account=response["payerAccount"], 
            payer_type=response["payerType"], 
            agreement_status=response["agreementStatus"],
            agreement_create_time=response["agreementCreateTime"],
            agreement_execute_time=response["agreementExecuteTime"],
            mode=response["mode"],
            verification_status=response["verificationStatus"],
        )

    def _create_payment_query_object(self, response: dict) -> Payment:
        return Payment(
            status_code=response["statusCode"],
            status_message=response["statusMessage"],
            payment_id=response["paymentID"],
            payer_reference=response["payerReference"],
            mode=response["mode"],
            payment_create_time=response["paymentCreateTime"],
            amount=response["amount"],
            currency=response["currency"],
            intent=response["intent"],
            merchant_invoice=response["merchantInvoice"],
            transaction_status=response["transactionStatus"],
            verification_status=response["verificationStatus"],
            agreement_status=response.get("agreementStatus"),
            agreement_create_time=response.get("agreementCreateTime"),
            agreement_execute_time=response.get("agreementExecuteTime"),
            agreement_id=response.get("agreementID"),
        )

    def _create_refund_execution_object(self, response: dict) -> RefundExecution:
        return RefundExecution(
            original_trx_id=response["originalTrxID"],
            refund_trx_id=response["refundTrxID"],
            transaction_status=response["transactionStatus"],
            amount=response["amount"],
            currency=response["currency"],
            completed_time=response["completedTime"],
            status_code=response["statusCode"],
            status_message=response["statusMessage"],
        )


    def _create_trx_object(self, response: dict) -> Transaction:
        return Transaction(
            # always-present fields → strict access
            trx_id=response["trxID"],
            initiation_time=response["initiationTime"],
            completed_time=response["completedTime"],
            transaction_type=response["transactionType"],
            customer_msisdn=response["customerMsisdn"],
            payer_account=response["payerAccount"],
            transaction_status=response["transactionStatus"],
            amount=response["amount"],
            currency=response["currency"],
            organization_short_code=response["organizationShortCode"],
            status_code=response["statusCode"],
            status_message=response["statusMessage"],

            # optional fields → safe access
            service_fee=response.get("serviceFee"),
            payer_type=response.get("payerType"),
            credited_amount=response.get("creditedAmount"),
            max_refundable_amount=response.get("maxRefundableAmount"),
            original_trx_amount=response.get("originalTrxAmount"),
        )


class Client(BaseClient):
    def __init__(self, token: Token) -> None:
        if not isinstance(token, Token):
            raise TypeError(
                    f"Client requires a Token instance, got {type(token).__name__} instead. "
                    f"Use AsyncToken with the asynchronous AsyncClient class."
                )
        self.token = token
        self._client = SyncClient(base_url=token.base_url)

    def close(self) -> None:
        """Closes the HTTP client connection.
        
        Should be called when done using the client to clean up resources.
        """
        self._client.close()

    def create_agreement(self, callback_url: str, payer_reference: str) -> AgreementCreation:
        """Creates a new bKash agreement for tokenized payments.
        
        Args:
            callback_url: URL where bKash redirects after user authentication
            payer_reference: Unique reference for the payer
        
        Returns:
            AgreementCreation: Agreement creation response with payment_id and bkash_url
        
        Raises:
            APIError: If agreement creation fails
        """
        data = {
            "mode": "0000",
            "callbackURL": callback_url,
            "payerReference": payer_reference,
        }
        response = self._client.post(url="/tokenized/checkout/create",headers=self.token.get_headers(), json=data)
        response.raise_for_status()
        response_json = response.json()
        raise_api_exception(response_json)
        return self._create_agreement_object(response_json)

    def create_payment(self, callback_url: str, payer_reference: str, amount: int, agreement_id: str | None = None, invoice_number: str | None = None, merchant_association_info: str | None = None) -> PaymentCreation: 
        """Creates a new bKash payment.
        
        Args:
            callback_url: URL where bKash redirects after user authentication
            payer_reference: Unique reference for the payer
            amount: Payment amount in BDT
            agreement_id: Optional agreement ID for tokenized payment (enables PIN-only flow)
            invoice_number: Optional merchant invoice number
            merchant_association_info: Optional merchant association information
        
        Returns:
            PaymentCreation: Payment creation response with payment_id and bkash_url
        
        Raises:
            APIError: If payment creation fails
        """
        data = {  
            "mode": "0011", # mode for url based payment without agreement
            "payerReference": str(payer_reference),
            "callbackURL": callback_url,
            "amount": amount,
            "currency": "BDT",   
            "intent": "sale",
            "merchantInvoiceNumber": "0000"
        }
        if agreement_id:
            data["mode"] = "0001" # change mode for agreement payment
            data["agreementID"] = agreement_id
        if invoice_number:
            data["merchantInvoiceNumber"] = invoice_number
        if merchant_association_info:
            data["merchantAssociationInfo"] = merchant_association_info 
        response = self._client.post(url="/tokenized/checkout/create",headers=self.token.get_headers(), json=data)
        response.raise_for_status()
        response_json = response.json()
        raise_api_exception(response_json)
        return self._create_payment_object(response_json)
    def _execute(self, payment_id: str) -> dict:
        """Executes Agreements and Payments via payment_id"""
        data = {
            "paymentID" : payment_id
        }
        response = self._client.post(url="/tokenized/checkout/execute",headers=self.token.get_headers(), json=data)
        response.raise_for_status()
        response_json = response.json()
        raise_api_exception(response_json)
        return response_json
    def execute_payment(self, payment_id: str) -> PaymentExecution:
        """Executes a payment after user authentication.
        
        Args:
            payment_id: The payment ID from create_payment()
        
        Returns:
            PaymentExecution: Execution response with transaction details and status
        
        Raises:
            APIError: If payment execution fails
        """
        response_json: dict = self._execute(payment_id)
        return self._create_payment_execution_object(response_json)

    def execute_agreement(self, payment_id: str) -> AgreementExecution:
        """Executes an agreement after user authentication.
        
        Args:
            payment_id: The payment ID from create_agreement()
        
        Returns:
            AgreementExecution: Execution response with agreement_id and status
        
        Raises:
            APIError: If agreement execution fails
        """
        response: dict = self._execute(payment_id)
        return self._create_agreement_execution_object(response)

    def cancel_agreement(self, agreement_id: str) -> AgreementCancellation:
        """Cancels an existing agreement.
        
        Args:
            agreement_id: The agreement ID to be cancelled
        
        Returns:
            AgreementCancellation: Cancellation response response with agreement_id and status
        
        Raises:
            APIError: If agreement cancellation fails
        """
        data = {
            'agreementID': agreement_id
        }
        response = self._client.post(url="/tokenized/checkout/agreement/cancel", headers=self.token.get_headers(), json=data)
        response.raise_for_status()
        response_json = response.json()
        raise_api_exception(response_json)
        return self._create_agreement_cancellation_object(response_json)

    def _query(self, payment_id: str) -> dict:
        """queries payments and agreements"""
        data = {
            "paymentID" : payment_id
        }
        response = self._client.post(url="/tokenized/checkout/payment/status",headers=self.token.get_headers(), json=data)
        response.raise_for_status()
        response_json = response.json()
        raise_api_exception(response_json)
        return response_json

    def query_agreement(self, payment_id: str) -> Agreement:
        """Queries the status and details of an agreement.
        
        Args:
            payment_id: The payment ID from create_agreement()
        
        Returns:
            Agreement: Agreement details including status and agreement_id
        
        Raises:
            APIError: If query fails
        """
        response_json: dict = self._query(payment_id)
        return self._create_agreement_query_object(response_json)

    def query_payment(self, payment_id: str) -> Payment:
        """Queries the status and details of a payment.
        
        Args:
            payment_id: The payment ID from create_payment()
        
        Returns:
            Payment: Payment details including status and transaction information
        
        Raises:
            APIError: If query fails
        """
        response: dict = self._query(payment_id)
        return self._create_payment_query_object(response)

    def execute_refund(self, payment_id: str, trx_id: str, refund_amount: int, sku: str | None = None, reason: str | None = None) -> RefundExecution:
        """Executes a refund for a completed payment.
        
        Args:
            payment_id: The payment ID from the original payment
            trx_id: The transaction ID from the original payment
            refund_amount: Amount to refund in BDT
            sku: Optional SKU/product identifier
            reason: Optional reason for the refund
        
        Returns:
            RefundExecution: Refund transaction details including refund_trx_id and status
        
        Raises:
            APIError: If refund fails
        """
        data = {
            "paymentID": payment_id,
            "trxID": trx_id,
            "amount": str(refund_amount),
            "sku": sku or "not_provided",
            "reason": reason or "not_provided"
        }
        response = self._client.post(url="/tokenized/checkout/payment/refund", headers=self.token.get_headers(), json=data)
        response.raise_for_status()
        response_json = response.json()
        raise_api_exception(response_json)
        return self._create_refund_execution_object(response_json)

    def search_trx(self, trx_id: str) -> Transaction:
        """Searches for a transaction by transaction ID.
        
        Args:
            trx_id: The transaction ID to search for
        
        Returns:
            Transaction: Transaction details including amount, status, and timestamps
        
        Raises:
            APIError: If transaction not found
        """
        data = {
            "trxID" : trx_id
        }
        response = self._client.post(url="/tokenized/checkout/general/searchTransaction",headers=self.token.get_headers(), json=data)
        response.raise_for_status()
        response_json = response.json()
        raise_api_exception(response_json)
        return self._create_trx_object(response_json)


class AsyncClient(BaseClient):
    def __init__(self, token: AsyncToken) -> None:
        if not isinstance(token, AsyncToken): # raise error if provided token is not async
            raise TypeError(
                f"AsyncClient requires an AsyncToken instance, got {type(token).__name__} instead. "
                f"Use Token with the synchronous Client class."
            )
        self.token = token
        self._client = HttpxAsyncClient(base_url=token.base_url)

    async def aclose(self) -> None:
        """Closes the async HTTP client connection.
        
        Should be called when done using the client to clean up resources.
        """
        await self._client.aclose()

    async def create_agreement(self, callback_url: str, payer_reference: str) -> AgreementCreation:
        """Creates a new bKash agreement for tokenized payments.
        
        Args:
            callback_url: URL where bKash redirects after user authentication
            payer_reference: Unique reference for the payer
        
        Returns:
            AgreementCreation: Agreement creation response with payment_id and bkash_url
        
        Raises:
            APIError: If agreement creation fails
        """
        data = {
            "mode": "0000",
            "callbackURL": callback_url,
            "payerReference": payer_reference,
        }
        response = await self._client.post(url="/tokenized/checkout/create",headers= await self.token.get_headers(), json=data)
        response.raise_for_status()
        response_json = response.json()
        raise_api_exception(response_json)
        return self._create_agreement_object(response_json)

    async def create_payment(self, callback_url: str, payer_reference: str, amount: int, agreement_id: str | None = None, invoice_number: str | None = None, merchant_association_info: str | None = None) -> PaymentCreation: 
        """Creates a new bKash payment.
        
        Args:
            callback_url: URL where bKash redirects after user authentication
            payer_reference: Unique reference for the payer
            amount: Payment amount in BDT
            agreement_id: Optional agreement ID for tokenized payment (enables PIN-only flow)
            invoice_number: Optional merchant invoice number
            merchant_association_info: Optional merchant association information
        
        Returns:
            PaymentCreation: Payment creation response with payment_id and bkash_url
        
        Raises:
            APIError: If payment creation fails
        """
        data = {  
            "mode": "0011", # mode for url based payment without agreement
            "payerReference": str(payer_reference),
            "callbackURL": callback_url,
            "amount": amount,
            "currency": "BDT",   
            "intent": "sale",
            "merchantInvoiceNumber": "0000"
        }
        if agreement_id:
            data["mode"] = "0001" # change mode for agreement payment
            data["agreementID"] = agreement_id
        if invoice_number:
            data["merchantInvoiceNumber"] = invoice_number
        if merchant_association_info:
            data["merchantAssociationInfo"] = merchant_association_info 
        response = await self._client.post(url="/tokenized/checkout/create",headers=await self.token.get_headers(), json=data)
        response.raise_for_status()
        response_json = response.json()
        raise_api_exception(response_json)
        return self._create_payment_object(response_json)
    async def _execute(self, payment_id: str) -> dict:
        """Executes Agreements and Payments via payment_id"""
        data = {
            "paymentID" : payment_id
        }
        response = await self._client.post(url="/tokenized/checkout/execute",headers= await self.token.get_headers(), json=data)
        response.raise_for_status()
        response_json = response.json()
        raise_api_exception(response_json)
        return response_json
    async def execute_payment(self, payment_id: str) -> PaymentExecution:
        """Executes a payment after user authentication.
        
        Args:
            payment_id: The payment ID from create_payment()
        
        Returns:
            PaymentExecution: Execution response with transaction details and status
        
        Raises:
            APIError: If payment execution fails
        """
        response_json: dict = await self._execute(payment_id)
        return self._create_payment_execution_object(response_json)

    async def execute_agreement(self, payment_id: str) -> AgreementExecution:
        """Executes an agreement after user authentication.
        
        Args:
            payment_id: The payment ID from create_agreement()
        
        Returns:
            AgreementExecution: Execution response with agreement_id and status
        
        Raises:
            APIError: If agreement execution fails
        """
        response: dict = await self._execute(payment_id)
        return self._create_agreement_execution_object(response)

    async def cancel_agreement(self, agreement_id: str) -> AgreementCancellation:
        """Cancels an existing agreement.
        
        Args:
            agreement_id: The agreement ID to be cancelled
        
        Returns:
            AgreementCancellation: Cancellation response response with agreement_id and status
        
        Raises:
            APIError: If agreement cancellation fails
        """
        data = {
            'agreementID': agreement_id
        }
        response = await self._client.post(url="/tokenized/checkout/agreement/cancel", headers= await self.token.get_headers(), json=data)
        response.raise_for_status()
        response_json = response.json()
        raise_api_exception(response_json)
        return self._create_agreement_cancellation_object(response_json)

    async def _query(self, payment_id: str) -> dict:
        """queries payments and agreements"""
        data = {
            "paymentID" : payment_id
        }
        response = await self._client.post(url="/tokenized/checkout/payment/status",headers=await self.token.get_headers(), json=data)
        response.raise_for_status()
        response_json = response.json()
        raise_api_exception(response_json)
        return response_json

    async def query_agreement(self, payment_id: str) -> Agreement:
        """Queries the status and details of an agreement.
        
        Args:
            payment_id: The payment ID from create_agreement()
        
        Returns:
            Agreement: Agreement details including status and agreement_id
        
        Raises:
            APIError: If query fails
        """
        response_json: dict = await self._query(payment_id)
        return self._create_agreement_query_object(response_json)

    async def query_payment(self, payment_id: str) -> Payment:
        """Queries the status and details of a payment.
        
        Args:
            payment_id: The payment ID from create_payment()
        
        Returns:
            Payment: Payment details including status and transaction information
        
        Raises:
            APIError: If query fails
        """
        response: dict = await self._query(payment_id)
        return self._create_payment_query_object(response)

    async def execute_refund(self, payment_id: str, trx_id: str, refund_amount: int, sku: str | None = None, reason: str | None = None) -> RefundExecution:
        """Executes a refund for a completed payment.
        
        Args:
            payment_id: The payment ID from the original payment
            trx_id: The transaction ID from the original payment
            refund_amount: Amount to refund in BDT
            sku: Optional SKU/product identifier
            reason: Optional reason for the refund
        
        Returns:
            Refund: Refund transaction details including refund_trx_id and status
        
        Raises:
            APIError: If refund fails
        """
        data = {
            "paymentID": payment_id,
            "trxID": trx_id,
            "amount": str(refund_amount),
            "sku": sku or "not_provided",
            "reason": reason or "not_provided"
        }
        response = await self._client.post(url="/tokenized/checkout/payment/refund", headers=await self.token.get_headers(), json=data)
        response.raise_for_status()
        response_json = response.json()
        raise_api_exception(response_json)
        return self._create_refund_execution_object(response_json)

    async def search_trx(self, trx_id: str) -> Transaction:
        """Searches for a transaction by transaction ID.
        
        Args:
            trx_id: The transaction ID to search for
        
        Returns:
            Transaction: Transaction details including amount, status, and timestamps
        
        Raises:
            APIError: If transaction not found
        """
        data = {
            "trxID" : trx_id
        }
        response = await self._client.post(url="/tokenized/checkout/general/searchTransaction",headers=await self.token.get_headers(), json=data)
        response.raise_for_status()
        response_json = response.json()
        raise_api_exception(response_json)
        return self._create_trx_object(response_json)
