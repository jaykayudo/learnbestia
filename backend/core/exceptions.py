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
