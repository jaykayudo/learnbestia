from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction as db_transaction
from rest_framework import serializers

from authentication.exceptions import InvalidCode, InvalidSession
from authentication.service import AuthService
from core.models import OTPToken, User


class ChangePasswordSerializer(serializers.Serializer):
    user = serializers.UUIDField()
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, attrs):
        try:
            user = User.objects.get(
                id=attrs["user"], auth_provider=User.PROVIDERS.EMAIL
            )
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "Account not Found"})
        if not user.check_password(attrs["current_password"]):
            raise serializers.ValidationError(
                {"detail": "Current Password is Incorrect"}, code=404
            )
        self.context["user"] = user
        return attrs

    def validate_new_password(self, password):
        try:
            password_validation.validate_password(password)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return password

    @db_transaction.atomic
    def save(self):
        user = self.context["user"]
        AuthService.set_new_password(user, self.validated_data["new_password"])


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs["email"]
        users = User.objects.filter(email=email, auth_provider=User.PROVIDERS.EMAIL)
        if not users.exists():
            raise serializers.ValidationError({"detail": "Account not Found"}, code=404)
        self.context["user"] = users.first()
        return attrs

    @db_transaction.atomic
    def save(self):
        user = self.context["user"]
        AuthService.send_reset_password_email(user)
        return {"id": user.id_str}


class ResetPasswordSerializer(serializers.Serializer):
    user = serializers.UUIDField()
    code = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        users = User.objects.filter(
            id=attrs["user"],
            auth_provider=User.PROVIDERS.EMAIL,
            is_active=True,
        )
        if not users.exists():
            raise serializers.ValidationError({"detail": "Account not Found"}, code=404)
        user = users.first()
        otps = OTPToken.objects.filter(user=user).order_by("-created_at")
        if not otps.exists():
            raise InvalidSession
        otp = otps.first()
        if not otp.verify_code(attrs["code"]):
            raise InvalidCode
        self.context["user"] = user
        return attrs

    def validate_password(self, password):
        try:
            password_validation.validate_password(password)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return password

    def save(self):
        user = self.context["user"]
        AuthService.set_new_password(user, self.validated_data["password"])
