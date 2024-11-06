from django.conf import settings
from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token
from rest_framework.exceptions import AuthenticationFailed


class Google:
    @classmethod
    def verify(cls, auth_token: str):
        try:
            google_data = verify_oauth2_token(auth_token, requests.Request())
            if google_data["aud"] != settings.GOOGLE_CLIENT_ID:
                raise Exception("Unknown Provider")

            return google_data
        except Exception as err:
            raise AuthenticationFailed({"detail": str(err)})

    @classmethod
    def connect(cls, auth_token: str):
        pass
