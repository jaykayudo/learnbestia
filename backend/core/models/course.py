# module that deals with everything regarding the context of a course

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _

from .base import BaseItem, BaseModel, OrderField
from .user import Instructor, User


class ContentTypeChoice(models.TextChoices):
    VIDEO = "video", "Video"
    BOOK = "book", "Book"


class ResourceType(models.TextChoices):
    LINK = "link", "Link"


class CourseStudentStatus(models.IntegerField):
    NOT_STARTED = 0, "Not Started"
    IN_PROGRESS = 1, "In Progress"
    COMPLETED = 2, "Completed"


class CourseMessageType(models.TextChoices):
    AUDIO = "audio", "Audio"
    TEXT = "text", "Text"
    FILE = "file", "File"


class CourseCategory(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=400, unique=True)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Course(BaseModel):
    owner = models.ForeignKey(
        Instructor, related_name="courses", on_delete=models.PROTECT
    )
    title = models.CharField(_("Course Title"), max_length=300)
    description = models.TextField(_("Course Description"))
    price = models.DecimalField(_("Price"), max_digits=15, decimal_places=2)
    is_available = models.BooleanField(default=False)
    thumbnail = models.ImageField(upload_to="course_thumbnail", blank=True, null=True)
    category = models.ManyToManyField(CourseCategory, blank=True)
    co_instructors = models.ManyToManyField(
        Instructor, related_name="co_courses", blank=True
    )
    students = models.ManyToManyField(User, through="CourseStudent")

    @property
    def crypto_price(self):
        pass

    @property
    def content_counts(self):
        pass

    @property
    def video_counts(self):
        pass

    def is_instructor(self, instructor: Instructor) -> bool:
        return self.owner == instructor

    def is_co_instructor(self, instructor: Instructor) -> bool:
        return self.co_instructors.filter(id=instructor.id).exists()

    def is_participant(self, user: User) -> bool:
        if self.students.filter(id=user.id).exists():
            return True
        if user.is_instructor:
            if self.is_instructor(user.instructor) or self.is_co_instructor(
                user.instructor
            ):
                return True
        return False

    def __str__(self) -> str:
        return self.title


class CourseObjective(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    order = OrderField(for_fields=["course"], verbose_name=_("Order"))

    class Meta:
        ordering = ["order"]


class CourseRequirement(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    order = OrderField(for_fields=["course"], verbose_name=_("Order"))

    class Meta:
        ordering = ["order"]


class CourseStudent(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    status = models.IntegerField(
        choices=CourseStudentStatus.choices,
        default=CourseStudentStatus.NOT_STARTED,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"], name="user_course_unique"
            )
        ]

    def __str__(self):
        return self.user.get_full_name()


class Module(BaseModel):
    course = models.ForeignKey(Course, related_name="modules", on_delete=models.CASCADE)
    title = models.CharField(_("Module Title"), max_length=300)
    order = OrderField(for_fields=["course"], verbose_name=_("Order"))
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.order}. {self.title}"

    class Meta:
        ordering = ["order"]


class Content(BaseModel):
    module = models.ForeignKey(
        Module, related_name="contents", on_delete=models.CASCADE
    )
    order = OrderField(for_fields=["module"], verbose_name=_("Order"))
    type = models.CharField(max_length=30, choices=ContentTypeChoice.choices)
    item_id = models.UUIDField()
    item_ct = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={"model__in": ["video", "text", "book"]},
    )
    item = GenericForeignKey("item_ct", "item_id")

    class Meta:
        ordering = ["order"]
        indexes = [
            models.Index(fields=["item_ct", "item_id"]),
        ]

    def __str__(self) -> str:
        return str(self.item)

    @property
    def title(self):
        return str(self.item.title)


class ContentProgress(BaseModel):
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    student = models.ForeignKey(CourseStudent, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    last_video_position = models.DurationField(blank=True, null=True)


class Video(BaseItem):
    file = models.FileField(
        upload_to=["videos"],
        validators=[FileExtensionValidator(["mp4", "webm", "mkv"])],
    )

    def __str__(self) -> str:
        return self.title


class Book(BaseItem):
    file = models.FileField(
        upload_to=["videos"],
        validators=[FileExtensionValidator(["pdf", "epub"])],
    )

    def __str__(self) -> str:
        return self.title


class Text(BaseItem):
    text = models.TextField()

    def __str__(self) -> str:
        return self.title


class Link(BaseItem):
    url = models.URLField("link")

    def __str__(self) -> str:
        return self.title


class Resource(BaseModel):
    content = models.ForeignKey(
        Content, related_name="resources", on_delete=models.CASCADE
    )
    type = models.CharField(max_length=20, choices=ResourceType.choices)
    order = OrderField(for_fields=["content"])
    item_id = models.UUIDField()
    item_ct = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={"model__in": ["link"]},
    )
    item = GenericForeignKey("item_ct", "item_id")

    @property
    def title(self):
        return self.item.title


# extras


class ContentNote(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    video_timestamp = models.DurationField(blank=True, null=True)
    note = models.TextField()


class CourseAnnouncement(BaseModel):
    poster = models.ForeignKey(Instructor, null=True, on_delete=models.SET_NULL)
    subject = models.CharField(max_length=200)
    message = models.TextField()

    def __str__(self):
        return self.subject


class CourseAnnouncementComment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    announcement = models.ForeignKey(CourseAnnouncement, on_delete=models.CASCADE)
    message = models.TextField()

    def __str__(self) -> str:
        return self.message


class CourseReview(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    message = models.TextField()

    def __str__(self) -> str:
        return self.message


class CourseQuestion(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self) -> str:
        return self.subject


class CourseQuestionComment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(CourseQuestion, on_delete=models.CASCADE)
    message = models.TextField()

    def __str__(self) -> str:
        return self.message


# course chat


class CourseChatRoom(BaseModel):
    course = models.OneToOneField(Course, on_delete=models.CASCADE)
    blocked_users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return str(self.course)


class CourseMessage(BaseModel):
    room = models.ForeignKey(CourseChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=CourseMessageType.choices)
    content_id = models.UUIDField()
    content_ct = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content = GenericForeignKey("content_ct", "content_id")


class MessageText(BaseModel):
    content = models.TextField()

    def json_data(self):
        return {"content": self.content}


class MessageAudio(BaseModel):
    file = models.FileField(upload_to="chat_audios")

    def json_data(self):
        return {"file": self.file.path}


class MessageImage(BaseModel):
    file = models.FileField(upload_to="chat_images")

    def json_data(self):
        return {"file": self.file.path}
