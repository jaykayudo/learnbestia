from rest_framework.exceptions import APIException


class ActionNotAllowed(APIException):
    status_code = 403
    default_code = "action_not_allowed"
    default_detail = "Action not allowed"
