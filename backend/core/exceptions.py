from rest_framework.exceptions import APIException


class CartIsEmpty(APIException):
    status_code = 400
    default_code = "cart_is_empty"
    default_detail = "Cart is empty"


class CouponIsInvalid(APIException):
    status_code = 400
    default_code = "invalid_coupon"
    default_detail = "Invalid coupon"


class InvalidTransaction(APIException):
    status_code = 400
    default_code = "invalid_transaction"
    default_detail = "Invalid Transaction"


class TransactionInitializationError(APIException):
    status_code = 500
    default_code = "tx_initialization_error"
    default_detail = "Could not initialize transaction"


class TransactionVerificationFailure(APIException):
    status_code = 400
    default_code = "tx_verification_failed"
    default_detail = "transaction verification failure"
