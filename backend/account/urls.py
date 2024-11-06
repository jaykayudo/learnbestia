from django.urls import path

from . import views

urlpatterns = [
    path("orders/", views.OrderHistoryListAPIView.as_view(), name="orders"),
    path("courses/", views.CourseListAPIView.as_view(), name="courses"),
    path(
        "courses/<uuid:course>/",
        views.CourseDetailsAPIView.as_view(),
        name="course_details",
    ),
    path(
        "courses/<uuid:course>/modules/",
        views.CourseModulesListAPIView.as_view(),
        name="course_modules",
    ),
    path(
        "courses/<uuid:course>/content/<uuid:content>/",
        views.CourseContentDetailsAPIView.as_view(),
        name="course_contents",
    ),
    path(
        "courses/<uuid:course>/content/<uuid:content>/notes/",
        views.CourseContentNoteListCreateAPIView.as_view(),
        name="course_content_notes",
    ),
    path(
        "courses/<uuid:course>/announcements/",
        views.CourseAnnouncementListAPIView.as_view(),
        name="course_announcements",
    ),
    path(
        "courses/<uuid:course>/announcements/<uuid:announcement>/comments/",
        views.CourseAnnouncementCommentsListCreateView.as_view(),
        name="course_announcement_comments",
    ),
    path(
        "courses/<uuid:course>/questions/",
        views.CourseQuestionListCreateAPIView.as_view(),
        name="course_questions",
    ),
    path(
        "courses/<uuid:course>/questions/<uuid:question>/comments/",
        views.CourseQuestionCommentListCreateAPIView.as_view(),
        name="course_question_comments",
    ),
    path(
        "courses/<uuid:course>/messages/",
        views.CourseChatMessagesListAPIView.as_view(),
        name="course_messages",
    ),
]
