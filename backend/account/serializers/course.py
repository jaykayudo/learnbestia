from rest_framework import serializers

from account.service import AccountService
from core.models import course
from core.serializers import user as user_serializer


class SimpleCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = course.Course
        fields = ["id", "title", "description", "price", "thumbnail"]


class CourseChatRoomSerializer(serializers.ModelSerializer):
    blocked_users = user_serializer.UserSerializer(many=True)

    class Meta:
        model = course.CourseChatRoom
        fields = ["id", "blocked_users"]


class CourseSerializer(serializers.ModelSerializer):
    chatroom = serializers.SerializerMethodField()

    class Meta:
        model = course.Course
        fields = "__all__"

    def get_chatroom(self, obj):
        chatroom = AccountService.get_course_chat_room(obj)
        data = CourseChatRoomSerializer(chatroom).data
        return data


class CourseModuleSerializer(serializers.ModelSerializer):
    contents = serializers.SerializerMethodField()

    class Meta:
        model = course.Module
        fields = ["title", "order", "description"]

    def get_contents(self, obj):
        contents = AccountService.get_module_contents(obj)
        data = SimpleContentSerializer(contents, many=True).data
        return data


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = course.Video
        fields = ["title", "file"]


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = course.Book
        fields = ["title", "file"]


class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = course.Text
        fields = ["title", "text"]


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = course.Link
        fields = ["title", "url"]


class ItemSerializer(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, course.Video):
            return VideoSerializer(value).data
        elif isinstance(value, course.Book):
            return BookSerializer(value).data
        elif isinstance(value, course.Text):
            return TextSerializer(value).data
        elif isinstance(value, course.Link):
            return LinkSerializer(value).data
        else:
            raise serializers.ValidationError("Unexpected content")


class ResourceItemSerializer(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, course.Link):
            return LinkSerializer(value).data
        raise serializers.ValidationError("Unexpected content")


class SimpleContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = course.Content
        fields = ["id", "order", "type", "title"]


class ContentSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = course.Content
        fields = ["id", "order", "type", "item"]


class ContentNoteSerializer(serializers.ModelSerializer):
    user = user_serializer.UserSerializer(read_only=True)

    class Meta:
        model = course.ContentNote
        fields = ["id", "user", "video_timestamp", "note"]


class ContentResourceSerializer(serializers.ModelSerializer):
    item = ResourceItemSerializer()

    class Meta:
        model = course.Resource
        fields = ["id", "type", "order", "item"]


class CourseQuestionSerializer(serializers.ModelSerializer):
    user = user_serializer.RelatedUserSerializer(read_only=True)

    class Meta:
        model = course.CourseQuestion
        fields = ["id", "user", "subject", "description", "created_at"]


class CourseQuestionCommentSerializer(serializers.ModelSerializer):
    user = user_serializer.RelatedUserSerializer(read_only=True)

    class Meta:
        model = course.CourseQuestionComment
        fields = ["id", "user", "message", "created_at"]


class MessageTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = course.MessageText
        fields = ["id", "content", "created_at"]


class MessageAudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = course.MessageAudio
        fields = ["id", "file", "created_at"]


class MessageImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = course.MessageImage
        fields = ["id", "file", "created_at"]


class MessageContentSerializer(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, course.MessageText):
            return MessageTextSerializer(value).data
        elif isinstance(value, course.MessageAudio):
            return MessageAudioSerializer(value).data
        elif isinstance(value, course.MessageImage):
            return MessageImageSerializer(value).data
        raise serializers.ValidationError("Unexpected chat content")


class CourseMessageSerializer(serializers.ModelSerializer):
    user = user_serializer.RelatedUserSerializer()
    content = MessageContentSerializer()

    class Meta:
        model = course.CourseMessage
        fields = ["id", "user", "type", "content"]


class CourseAnnouncementSerializer(serializers.ModelSerializer):
    poster = user_serializer.InstructorSerializer()

    class Meta:
        model = course.CourseAnnouncement
        fields = ["id", "poster", "subject", "message"]


class CourseAnnouncementCommentSerializer(serializers.ModelSerializer):
    user = user_serializer.UserSerializer(read_only=True)

    class Meta:
        model = course.CourseAnnouncementComment
        fields = ["id", "user", "message"]
