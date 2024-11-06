from rest_framework import serializers

from core import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = "__all__"
        read_only_fields = ["id", "provider", "email", "is_instructor"]
        extra_kwargs = {"password": {"write_only": True}}
