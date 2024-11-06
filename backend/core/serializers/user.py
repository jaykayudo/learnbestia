from models import user
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user.User
        fields = ["id", "username", "first_name", "last_name"]

        def get_username(self, obj: user.User):
            if obj.email:
                return obj.email
            return obj.wallet_id


class InstructorSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = user.Instructor
        fields = ["user", "title", "bio", "is_verified"]


class RelatedUserSerializer(serializers.RelatedField):
    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return UserSerializer(value).data
