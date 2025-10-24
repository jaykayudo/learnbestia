from models import course, notification, user
from . import course as course_serializers
from . import user as user_serializers
from rest_framework import serializers


class RelateObjectField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, course.Course):
            return course_serializers.SimpleCourseSerializer(value).data
        elif isinstance(value, user.User):
            return user_serializers.UserSerializer(value).data
        else:
            return str(value)


class NotificationSerializer(serializers.ModelSerializer):
    related_content = RelateObjectField(read_only=True)

    class Meta:
        model = notification.Notification
        fields = [
            "id",
            "user",
            "title",
            "description",
            "priority",
            "notification_type",
            "is_read",
            "related_content",
            "created_at",
            "updated_at",
        ]
