from django.urls import path
from core.consumers.course import CourseConsumer

websocket_urlpatterns = [
    path("ws/course/<uuid:id>/", CourseConsumer.as_asgi()),
]
