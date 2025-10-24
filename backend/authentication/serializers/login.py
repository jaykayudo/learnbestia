from providers.ethereum import Ethereum
from providers.google import Google
from providers.polkadot import Polkadot
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from authentication.service import AuthService
from core.models import User

from .user import UserSerializer


class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        users = User.objects.filter(
            email=attrs["email"],
            auth_provider=User.PROVIDERS.EMAIL,
            is_active=True,
        )
        if not users.exists():
            raise AuthenticationFailed({"details": "Invalid Credentials"})
        user = users.first()
        if not user.check_password(attrs["password"]):
            raise AuthenticationFailed({"details": "Invalid Credentials"})
        self.context["user"] = user
        return attrs

    def save(self):
        user = self.context["user"]
        data = UserSerializer(user).data
        login_data = AuthService.login_user(user)
        return {**data, **login_data}


class GoogleLoginSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate(self, attrs):
        auth_token = attrs["auth_token"]
        user_data = Google.verify(auth_token)
        users = User.objects.filter(
            email=user_data["data"],
            auth_provider=User.PROVIDERS.GOOGLE,
            is_active=True,
        )
        if not users.exists():
            raise AuthenticationFailed({"details": "Account not registered with us"})

        self.context["user"] = users.first()
        return attrs

    def save(self):
        user = self.context["user"]
        data = UserSerializer(user).data
        login_data = AuthService.login_user(user)
        return {**data, **login_data}


class EthereumLoginSerializer(serializers.Serializer):
    message = serializers.CharField()
    signature = serializers.CharField()

    def validate(self, attrs):
        request = self.context["request"]
        address = Ethereum.verify(
            message=attrs["message"],
            signature=attrs["signature"],
            request=request,
        )
        users = User.objects.filter(
            wallet_id=address, provider=User.PROVIDERS.ETHEREUM, is_active=True
        )
        if not users.exists():
            raise AuthenticationFailed({"details": "Account not registered with us"})

        self.context["user"] = users.first()
        return attrs

    def save(self):
        user = self.context["user"]
        data = UserSerializer(user).data
        login_data = AuthService.login_user(user)
        return {**data, **login_data}


class PolkadotLoginSerializer(serializers.Serializer):
    message = serializers.CharField()
    signature = serializers.CharField()

    def validate(self, attrs):
        request = self.context["request"]
        address = Polkadot.verify(
            message=attrs["message"],
            signature=attrs["signature"],
            request=request,
        )
        users = User.objects.filter(
            wallet_id=address, provider=User.PROVIDERS.POLKADOT, is_active=True
        )
        if not users.exists():
            raise AuthenticationFailed({"details": "Account not registered with us"})

        self.context["user"] = users.first()
        return attrs

    def save(self):
        user = self.context["user"]
        data = UserSerializer(user).data
        login_data = AuthService.login_user(user)
        return {**data, **login_data}
