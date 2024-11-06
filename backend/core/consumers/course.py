from typing import Literal

from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from loguru import logger
from pydantic import BaseModel

from core.models import course as course_models
from core.utils import get_course_channel_name


class CourseEvent(BaseModel):
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
        self.course = await database_sync_to_async(self.is_course_participant)(
            user
        )
        self.user = user
        self.course_name = get_course_channel_name(self.course_id)
        await self.channel_layer.group_add(self.course_name, self.channel_name)
        logger.info(f"{user} is connected to course {self.course_name}")
        await self.accept()

    async def send_message(self, event):
        await self.send_json(event["data"])

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.course_name, self.channel_name
        )
        self.close(close_code)
