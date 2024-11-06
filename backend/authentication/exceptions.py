from rest_framework.exceptions import APIException


class InvalidSession(APIException):
    status_code = 403
    default_code = "invalid_session"
    default_detail = "Invalid Session"


class InvalidCode(APIException):
    status_code = 403
    default_code = "invalid_code"
    default_detail = "Code is Invalid"
