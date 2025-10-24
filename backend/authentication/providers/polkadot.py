from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import HttpRequest
from siws import SiwsMessage


class Polkadot:
    @classmethod
    def verify(cls, *, message: str, signature: str, request: HttpRequest):
        # TODO: Provide check for nonce using CSRF token.
        siws = SiwsMessage(message=message)
        domain = request.get_host()
        try:
            siws.verify(signature=signature, public_key=siws.address, domain=domain)
        except Exception as err:
            raise AuthenticationFailed({"detail": str(err)})
        return siws.address

    @classmethod
    def connect(cls):
        pass
