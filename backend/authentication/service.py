from django.conf import settings
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from core import models


class AuthService:
    @classmethod
    def register_user(cls, data: dict):
        user = models.User()
        user.first_name = data["first_name"]
        user.last_name = data.get("last_name", "")
        user.email = data["email"]
        user.set_password(data["password"])
        user.save()
        return user

    @classmethod
    def register_social_user(cls, data: dict):
        assert "email" in data, "Email must be provided"
        assert "name" in data, "Name must be provided"
        assert "provider" in data, "Provider must be provided"

        # check if user of provider in db
        users = models.User.objects.filter(email=data["email"])
        if users.exists():
            user = users.first()
            raise serializers.ValidationError(
                {
                    "detail": (
                        "User with similar email already"
                        "exist for {user.auth_provider} provider"
                    )
                }
            )
        user = models.User()
        user.email = data["email"]
        user.first_name = data["name"]
        user.auth_provider = data["provider"]
        user.set_password(settings.OAUTH_SECRET)
        user.save()
        return user

    @classmethod
    def register_blockchain_account(cls, **data: dict):
        assert "address" in data, "Email must be provided"
        assert "first_name" in data, "First name must be provided"
        assert "provider" in data, "Provider must be provided"

        users = models.User.objects.filter(wallet_id=data["address"])
        if users.exists():
            user = users.first()
            raise serializers.ValidationError(
                {
                    "detail": (
                        "User with wallet id already exist"
                        f" for {user.auth_provider} provider"
                    )
                }
            )
        user = models.User()
        user.wallet_id = data["address"]
        user.first_name = data["first_name"]
        user.last_name = data.get("last_name")
        user.auth_provider = data["provider"]
        user.save()
        return user

    @classmethod
    def login_user(cls, user: models.User):
        data = RefreshToken.for_user(user)
        return {"access": str(data.access_token), "refresh": str(data)}

    @classmethod
    def set_new_password(cls, user: models.User, password: str):
        # TODO: clear all login session
        user.set_password(password)
        user.save()

    @classmethod
    def send_reset_password_email(cls, user: models.User):
        code, otp = models.OTPToken.objects.create(
            user=user, reason=models.OTPToken.OTP_REASONS.PASSWORD_RESET
        )
        user.email_user(
            "Password Reset",
            (
                "You have requested to reset your password."
                f"Use this code to reset it {code}"
                "If this is not you, ignore this email or contact support"
            ),
        )
        return otp
