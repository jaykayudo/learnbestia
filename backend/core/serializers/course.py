from models import course
from rest_framework import serializers

from .user import InstructorSerializer, UserSerializer


class CourseCategorySerializer(serializers.ModelSerializer):
    course_number = serializers.SerializerMethodField()

    class Meta:
        model = course.CourseCategory
        fields = ["name", "slug", "course_number"]

    def get_course_number(self, obj):
        return obj.course_set.count()


class SimpleCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = course.Course
        fields = ["id", "title", "description", "price", "thumbnail"]


class CourseObjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = course.CourseObjective
        fields = ["title", "description", "order"]


class CourseRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = course.CourseRequirement
        fields = ["title", "description", "order"]


class CourseSerializer(serializers.ModelSerializer):
    owner = InstructorSerializer()
    co_instructors = InstructorSerializer(many=True)
    students_count = serializers.SerializerMethodField()
    category = serializers.StringRelatedField(many=True)
    objectives = serializers.SerializerMethodField()
    requirements = serializers.SerializerMethodField()

    class Meta:
        model = course.Course
        fields = "__all__"

    def get_students_count(self, obj: course.Course):
        return obj.students.count()

    def get_objectives(self, obj: course.Course):
        objectives = course.CourseObjective.objects.filter(
            course=obj
        ).order_by("order")
        data = CourseObjectiveSerializer(objectives, many=True).data
        return data

    def get_requirements(self, obj: course.Course):
        requirements = course.CourseRequirement.objects.filter(
            course=obj
        ).order_by("order")
        data = CourseRequirementSerializer(requirements, many=True).data
        return data


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = course.Module
        fields = "__all__"


class ContentSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = course.Content
        fields = ["title", "type"]

    def get_title(self, obj):
        return obj.item.title


class CourseReviewsSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = course.CourseReview
        fields = "__all__"
