# file for all abstract and base models
import uuid
from typing import Any

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class NotificationType(models.TextChoices):
    AUTH = "auth", "Auth"


class BaseModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ("-created_at",)

    @property
    def id_str(self):
        return str(self.id)


class OrderField(models.PositiveIntegerField):
    def __init__(self, for_fields=None, *args, **kwargs) -> None:
        self.for_fields = for_fields
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance: models.Model, add: bool) -> Any:
        if getattr(model_instance, self.attname) is None:
            try:
                qs = self.model.objects.all()
                if self.for_fields:
                    query = {
                        field: getattr(model_instance, field)
                        for field in self.for_fields
                    }
                    qs = qs.filter(**query)
                    # get the order of the last item
                last_item = qs.latest(self.attname)
                value = last_item.order + 1
            except ObjectDoesNotExist:
                value = 0
            setattr(model_instance, self.attname, value)
            return value
        return super().pre_save(model_instance, add)


class BaseItem(BaseModel):
    owner = models.ForeignKey("User", null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=200)

    class Meta:
        ordering = ("-created_at",)
        abstract = True

    def __str__(self) -> str:
        return self.title


class BaseNotification(BaseModel):
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=500)
    target_id = models.UUIDField()
    target_ct = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    target = GenericForeignKey("target_ct", "target_id")

    class Meta:
        ordering = ("-created_at",)
        abstract = True

    def __str__(self) -> str:
        return self.title

    def send_notification(self):
        raise NotImplementedError
