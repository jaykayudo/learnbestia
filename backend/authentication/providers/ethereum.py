from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import HttpRequest
from siwe import SiweMessage


class Ethereum:
    @classmethod
    def verify(cls, *, message: str, signature: str, request: HttpRequest):
        # TODO: Provide check for nonce using CSRF token.
        siwe = SiweMessage.from_message(message)
        domain = request.get_host()
        try:
            siwe.verify(signature=signature, domain=domain)
        except Exception as err:
            raise AuthenticationFailed({"detail": str(err)})
        return siwe.address

    @classmethod
    def connect(cls, data: dict):
        pass
