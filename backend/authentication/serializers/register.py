from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction as db_transaction
from providers.ethereum import Ethereum
from providers.google import Google
from providers.polkadot import Polkadot
from rest_framework import serializers

from authentication.service import AuthService
from core.models import User

from .user import UserSerializer


class GoogleRegisterSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate(self, attrs):
        auth_token = attrs["auth_token"]
        user_data = Google.verify(auth_token)
        provider = User.PROVIDERS.GOOGLE
        self.context["user_data"] = {**user_data, "provider": provider}
        return attrs

    @db_transaction.atomic
    def save(self):
        user = AuthService.register_social_user(self.context["user_data"])
        data = UserSerializer(user).data
        login_data = AuthService.login_user(user)
        return {**data, **login_data}


class EmailRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"detail": "User with email already exists"}
            )
        return email

    def validate_password(self, password):
        try:
            password_validation.validate_password(password)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return password

    @db_transaction.atomic
    def save(self):
        user = AuthService.register_user(self.validated_data)
        data = UserSerializer(user).data
        login_data = AuthService.login_user(user)
        return {**data, **login_data}


class EthereumRegisterSerializer(serializers.Serializer):
    message = serializers.CharField()
    signature = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField(required=False)

    def validate(self, attrs):
        request = self.context["request"]
        address = Ethereum.verify(
            message=attrs["message"],
            signature=attrs["signature"],
            request=request,
        )
        self.context["address"] = address
        return attrs

    @db_transaction.atomic
    def save(self):
        user = AuthService.register_blockchain_account(
            first_name=self.validated_data["first_name"],
            last_name=self.validated_data.get("last_name", ""),
            address=self.context["address"],
            provider=User.PROVIDERS.ETHEREUM,
        )
        login_data = AuthService.login_user(user)
        return {**user, **login_data}


class PolkadotRegisterSerializer(serializers.Serializer):
    message = serializers.CharField()
    signature = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField(required=False)

    def validate(self, attrs):
        request = self.context["request"]
        address = Polkadot.verify(
            message=attrs["message"],
            signature=attrs["signature"],
            request=request,
        )
        self.context["address"] = address
        return attrs

    @db_transaction.atomic
    def save(self):
        user = AuthService.register_blockchain_account(
            first_name=self.validated_data["first_name"],
            last_name=self.validated_data.get("last_name", ""),
            address=self.context["address"],
            provider=User.PROVIDERS.POLKADOT,
        )
        login_data = AuthService.login_user(user)
        return {**user, **login_data}
