from rest_framework import generics
from rest_framework.response import Response

from core.utils import CorePagination, MessagePagination

from . import permissions
from .serializers import course, sales
from .service import AccountService


class OrderHistoryListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsActiveUser]
    serializer_class = sales.OrderSerializer

    def get_queryset(self):
        return AccountService.get_order_history(self.request.user)


class CourseListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsActiveUser]
    serializer_class = course.SimpleCourseSerializer
    pagination_class = CorePagination

    def get_queryset(self):
        return AccountService.get_user_courses(self.request.user)


class CourseDetailsAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsCourseStudent]
    serializer_class = course.CourseSerializer
    lookup_field = "course"


class CourseModulesListAPIView(
    permissions.CourseStudentPermissionMixin, generics.ListAPIView
):
    serializer_class = course.CourseModuleSerializer

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return AccountService.get_course_modules(self.course)


class CourseContentDetailsAPIView(
    permissions.CourseStudentPermissionMixin, generics.RetrieveAPIView
):
    serializer_class = course.ContentSerializer

    def get_object(self):
        return AccountService.get_content(self.kwargs, self.course)


class CourseAnnouncementListAPIView(
    permissions.CourseStudentPermissionMixin, generics.ListAPIView
):
    serializer_class = course.CourseAnnouncementSerializer
    pagination_class = CorePagination

    def get_queryset(self):
        return AccountService.get_course_announcements(self.course)


class CourseAnnouncementCommentsListCreateView(
    permissions.CourseStudentPermissionMixin, generics.ListCreateAPIView
):
    serializer_class = course.CourseAnnouncementCommentSerializer

    def get_object(self):
        return AccountService.get_announcement_detail(self.course, self.kwargs)

    def get_queryset(self):
        obj = self.get_object()
        return AccountService.get_announcement_comments(obj)

    def create(self, request, *args, **kwargs):
        announcement = self.get_object()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, announcement=announcement)
        return Response(serializer.data)


class CourseQuestionListCreateAPIView(
    permissions.CourseStudentPermissionMixin, generics.ListCreateAPIView
):
    pagination_class = CorePagination
    serializer_class = course.CourseQuestionSerializer

    def get_queryset(self):
        return AccountService.get_course_questions(self.course)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, course=self.course)
        return Response(serializer.data)


class CourseQuestionCommentListCreateAPIView(
    permissions.CourseStudentPermissionMixin, generics.ListCreateAPIView
):
    serializer_class = course.CourseQuestionCommentSerializer
    pagination_class = MessagePagination

    def get_object(self):
        return AccountService.get_question_details(self.course, self.kwargs)

    def create(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, question=obj)
        return Response(serializer.data)

    def get_queryset(self):
        return AccountService.get_course_questions_comment(self.get_object())


class CourseContentNoteListCreateAPIView(
    permissions.CourseStudentPermissionMixin, generics.ListCreateAPIView
):
    serializer_class = course.ContentNoteSerializer

    def create(self, request, *args, **kwargs):
        content = self.get_object()
        serializer = self.serializer_class(data=request.user)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, content=content)
        return Response(serializer.data)

    def get_object(self):
        return AccountService.get_content(self.kwargs, self.course)

    def get_queryset(self):
        return AccountService.get_content_notes(
            self.request.user, self.get_object()
        )


class CourseChatMessagesListAPIView(
    permissions.CourseStudentPermissionMixin, generics.ListAPIView
):
    serializer_class = course.CourseMessageSerializer
    pagination_class = MessagePagination

    def get_queryset(self):
        return AccountService.get_course_chat_messages(self.course)
