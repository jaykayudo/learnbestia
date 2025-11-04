from typing import Callable

""""
All the data structure of all the messages sent via channels.
Chat: (Bi-directional)
 - sender (username)
 - message (text)
 - message_type ('text', 'file')
 - file 
 

CourseAnnouncement: (uni-directional)
- subject
- message

CourseAnnouncementComment: (bi-directional)
- announcement_id (announcement)
- sender (username)
- message (txt)

CourseQuestion: (uni-directional)
- subject
- message
"""


HANDLERS_DICT = {
    "chat",
    "announcement",
    "announcement_comment",
    "question",
    "question_comment",
}

import enum
import uuid
from asgiref.sync import async_to_sync
from typing import Any

from channels.layers import get_channel_layer
from django.contrib.contenttypes.models import ContentType
from django.db import transaction, models

from core.utils import get_course_channel_name, base64_to_file
from core.models import course
from core.serializers import course as course_serializers


class InvalidDataException(Exception):
    pass


class SocketTypes(enum.StrEnum):
    SEND_MESSAGE = "send.message"


class StrEventTypes(enum.StrEnum):
    announcement = "announcement"
    question = "question"


class EventHandler:
    @classmethod
    def process_data(cls, course_id: str, data: dict) -> dict | None:
        raise NotImplementedError


class ChatHandler(EventHandler):
    @classmethod
    @transaction.atomic
    def process_data(cls, course_id: str, data: dict) -> dict | None:
        try:
            room_id = data["room_id"]
            obj = course.CourseChatRoom.objects.get(id=room_id)
            user = data["user"]

            chat_data = cls.create_chat_data(data)

            if not chat_data:
                raise InvalidDataException

            ct, ct_obj = chat_data
            message_obj = course.CourseMessage.objects.create(
                course=obj, user=user, content_id=ct_obj.id, content_ct=ct
            )
            return {
                "id": message_obj.id_str,
                "user": str(user),
                **ct_obj.json_data(),
                "created_at": message_obj.created_at.strftime("%d/%m/%Y, %H:%M:%S"),
            }
        except course.CourseChatRoom.DoesNotExist:
            return {"type": "error", "data": "course chat does not exist"}
        except InvalidDataException:
            return {"type": "error", "data": "provided data is invalid"}
        except KeyError:
            return {"type": "error", "data": "provided data is invalid"}
        except Exception:
            return {"type": "error", "data": "unknown"}

    @classmethod
    def create_chat_data(data: dict) -> tuple[ContentType, models.Model] | None:
        type = data["type"]
        if type == course.CourseMessageType.AUDIO:
            # create the file from sent base64
            file = base64_to_file(data["file"], "AUDIO_")
            # create a message audio instance
            obj = course.MessageAudio.objects.create(file=file)
            # get the message audio content type
            ct = ContentType.objects.get_for_model(course.MessageAudio)
            return ct, obj
        elif type == course.CourseMessageType.TEXT:
            # create a message text instance
            obj = course.MessageText.objects.create(content=data["content"])
            # get the message text content type
            ct = ContentType.objects.get_for_model(course.MessageText)
            return ct, obj
        elif type == course.CourseMessageType.FILE:
            # create the file from sent base64
            file = base64_to_file(data["file"], "IMAGE_")
            # create a message image instance
            obj = course.MessageImage.objects.create(file=file)
            # get the message image content type
            ct = ContentType.objects.get_for_model(course.MessageImage)
            return ct, obj

        return None


class QuestionCommentHandler(EventHandler):
    @classmethod
    @transaction.atomic
    def process_data(cls, course_id: str, data: dict) -> dict | None:
        try:
            question = course.CourseQuestion.objects.get(id=data["question_id"])
            user = data["user"]
            message = data["message"]
            comment = course.CourseQuestionComment.objects.create(
                user=user, question=question, message=message
            )
            return {
                "id": comment.id_str,
                "user": str(user),
                "question": question.id_str,
                "message": comment.message,
                "created_at": comment.created_at.strftime("%d/%m/%Y, %H:%M:%S"),
            }

        except course.CourseQuestion.DoesNotExist:
            return {"type": "error", "data": "course question does not exist"}
        except KeyError:
            return {"type": "error", "data": "provided data is invalid"}


class SocketService:
    @classmethod
    def channel_layer(cls):
        return get_channel_layer()

    @classmethod
    def send_message(
        cls, course_id: str, event_type: StrEventTypes, data: dict[str, Any]
    ):
        async_to_sync(cls.channel_layer().group_send)(
            get_course_channel_name(course_id),
            {
                "type": SocketTypes.SEND_MESSAGE,
                "data": {"type": str(event_type), "data": data},
            },
        )


EVENT_HANDLERS = {"chat": ChatHandler, "question_comment": QuestionCommentHandler}
