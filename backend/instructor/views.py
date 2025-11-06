# Create your views here.
from rest_framework import generics
from rest_framework.response import Response

from core.models.user import Instructor
from instructor.permissions import IsInstructor
from instructor.services.dashboard import DashboardService


class DashboardAPIView(generics.GenericAPIView):
    permission_classes = [IsInstructor]

    def get(self, request):
        instructor = Instructor.objects.get(user=request.user)
        data = {
            "number_of_students": DashboardService.get_number_of_students(instructor),
            "number_of_courses": DashboardService.get_number_of_courses(instructor),
            "total_earnings": DashboardService.get_total_earnings(instructor),
        }
        return Response(data)
