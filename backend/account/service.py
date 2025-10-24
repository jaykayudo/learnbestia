from core.models import (
    course as course_models,
)
from core.models import (
    sales as sales_models,
)
from core.models import (
    user as user_models,
)

from . import exceptions


class AccountService:
    @classmethod
    def get_user_profile(cls, user: user_models.User):
        # generate more profile data
        return {"user": user}

    @classmethod
    def get_user_courses(cls, user: user_models.User):
        courses = user.course_set.all()
        return courses

    @classmethod
    def get_order_history(cls, user: user_models.User):
        orders = sales_models.Order.objects.filter(user=user).order_by("-created_at")
        return orders

    @classmethod
    def get_course_modules(cls, course: course_models.Course):
        modules = course_models.Module.objects.filter(course=course).order_by("order")
        return modules

    @classmethod
    def get_module_contents(cls, module: course_models.Module):
        contents = course_models.Content.objects.filter(module=module).order_by("order")
        return contents

    @classmethod
    def get_content(cls, kwargs: dict, course: course_models.Course):
        if not (content := kwargs.get("content")):
            raise exceptions.ActionNotAllowed
        try:
            return course_models.Content.objects.get(id=content, module__course=course)
        except course_models.Content.DoesNotExist:
            raise exceptions.ActionNotAllowed

    @classmethod
    def get_course_announcements(cls, course: course_models.Course):
        announcements = course_models.CourseAnnouncement.objects.filter(
            course=course
        ).order_by("-created_at")
        return announcements

    @classmethod
    def get_announcement_detail(cls, course: course_models.Course, kwargs: dict):
        try:
            return course_models.CourseAnnouncement.objects.get(
                id=kwargs.get("announcement"), course=course
            )
        except course_models.CourseAnnouncement.DoesNotExist:
            raise exceptions.ActionNotAllowed

    @classmethod
    def get_announcement_comments(cls, announcement: course_models.CourseAnnouncement):
        return course_models.CourseAnnouncementComment.objects.filter(
            announcement=announcement
        )

    @classmethod
    def get_course_questions(cls, course: course_models.Course):
        return course_models.CourseQuestion.objects.filter(course=course).order_by(
            "-created_at"
        )

    @classmethod
    def get_course_questions_comment(cls, question: course_models.CourseQuestion):
        return course_models.CourseQuestionComment.objects.filter(
            question=question
        ).order_by("-created_at")

    @classmethod
    def get_question_details(cls, course: course_models.Course, kwargs: dict):
        try:
            return course_models.CourseQuestion.objects.get(
                id=kwargs.get("question"), course=course
            )
        except course_models.CourseQuestion.DoesNotExist:
            raise exceptions.ActionNotAllowed

    @classmethod
    def get_content_notes(cls, user: user_models.User, content: course_models.Content):
        return course_models.ContentNote.objects.filter(
            user=user, content=content
        ).order_by("-created_at")

    @classmethod
    def get_course_chat_room(cls, course: course_models.Course):
        chat_room = course_models.CourseChatRoom.objects.get_or_create(course=course)
        return chat_room

    @classmethod
    def get_course_chat_messages(cls, course: course_models.Course):
        chat_room = cls.get_course_chat_room(course)
        messages = course_models.CourseMessage.objects.filter(room=chat_room).order_by(
            "-created_at"
        )
        return messages
