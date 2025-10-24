from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from .base import BaseModel
from .user import User


class NotificationPrority(models.IntegerChoices):
    LOW = 0, "Low"
    MEDIUM = 1, "Medium"
    HIGH = 2, "High"
    URGENT = 3, "Urgent"


class NotificationType(models.TextChoices):
    INFO = "info", "Info"
    WARNING = "warning", "Warning"
    ERROR = "error", "Error"
    SUCCESS = "success", "Success"


class Notification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    object_id = models.UUIDField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    related_content = GenericForeignKey("content_type", "object_id")
    priority = models.IntegerField(
        choices=NotificationPrority.choices, default=NotificationPrority.MEDIUM
    )
    notification_type = models.CharField(
        max_length=20, choices=NotificationType.choices, default=NotificationType.INFO
    )
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        indexes = [models.Index(fields=["content_type", "object_id"])]
