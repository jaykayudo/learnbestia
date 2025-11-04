from typing import Literal

from pydantic import BaseModel, ValidationError


from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from loguru import logger

from core.models import course as course_models
from core.utils import get_course_channel_name
from core.consumers.service import EVENT_HANDLERS


class Event(BaseModel):
    type: Literal[
        "chat",
        "announcement",
        "announcement_comment",
        "question",
        "question_comment",
    ]
    data: dict


class CourseConsumer(AsyncJsonWebsocketConsumer):
    def is_course_participant(self, user):
        try:
            course = course_models.Course.objects.get(id=self.course_id)
            if not course.is_participant(user):
                raise StopConsumer
            return course
        except course_models.Course.DoesNotExist:
            raise StopConsumer

    async def connect(self):
        self.course_id = self.scope["url_route"]["kwargs"]["id"]
        user = self.scope.get("user")
        if not user or user.is_anonymous:
            self.close()
        self.course = await database_sync_to_async(self.is_course_participant)(user)
        self.user = user
        self.course_name = get_course_channel_name(self.course_id)
        await self.channel_layer.group_add(self.course_name, self.channel_name)
        logger.info(f"{user} is connected to course {self.course_name}")
        await self.accept()

    async def send_message(self, event):
        """
        event format:
         - type: "question","announcement"
         - data: question_data or announcement_data
        e.g question_data:
            - id: uuid as str
            - course: uuid as str
            - subject: str
            - description: str
        e.g announcement_data:
            - id: uuid as str
            - poster: uuid as str
            - subject: str
            - message: str
        """
        await self.send_json(event["data"])

    async def receive_json(self, content, **kwargs):
        """
        The format of the received content will be;
        content: {
            'type': str
            'data': dict
        }
        """
        type = content["type"]
        data: dict = content["data"]
        # validate data received from room
        try:
            event = Event(type=type, data=data)
            user = self.user
            data = {"user": user, **data}
            if event.type in EVENT_HANDLERS:
                response = EVENT_HANDLERS[event.type].process_data(
                    self.course_id, event.data
                )
                if response:
                    await self.send_json(response)
        except ValidationError:
            await self.send_json({"type": "error", "data": "Error validating request"})

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.course_name, self.channel_name)
        self.close(close_code)
