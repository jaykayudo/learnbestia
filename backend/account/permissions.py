from rest_framework.permissions import BasePermission

from core.models.course import Course

from . import exceptions


class IsActiveUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsCourseStudent(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not (is_active_user := IsActiveUser().has_permission(request, view)):
            return is_active_user
        user = request.user
        flag = obj.students.filter(user=user).exists()
        return flag


class CourseStudentPermissionMixin:
    def get_course(self):
        if not (course := self.kwargs.get("course")):
            raise exceptions.ActionNotAllowed
        try:
            return Course.objects.get(id=course)
        except Course.DoesNotExist:
            raise exceptions.ActionNotAllowed

    def check_course_permissions(self, request):
        self.course = self.get_course()
        permission = IsCourseStudent()
        if not permission.has_object_permission(request, self, self.course):
            raise self.permission_denied(
                request,
                message=getattr(permission, "message", None),
                code=getattr(permission, "code", None),
            )

    def check_permissions(self, request):
        self.check_course_permissions(request)
        super().check_permissions(request)
