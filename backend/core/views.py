from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import course as course_models
from core.serializers import course as course_serializer
from core.serializers import sales as sales_serializer
from core.service import CoreService


class CourseCategoryListAPIView(generics.ListAPIView):
    serializer_class = course_serializer.CourseCategorySerializer

    @method_decorator(cache_page(60 * 60 * 2))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return course_models.CourseCategory.objects.all().order_by("name")


class CourseListAPIView(generics.ListAPIView):
    serializer_class = course_serializer.SimpleCourseSerializer

    def get_queryset(self):
        kwargs = {}
        if category_params := self.request.query_params.get("category"):
            try:
                category = course_models.CourseCategory.objects.get(
                    slug=category_params
                )
                kwargs["category"] = category
            except Exception:
                pass
        return course_models.Course.objects.filter(**kwargs)


class CourseDetailAPIView(generics.RetrieveAPIView):
    serializer_class = course_serializer.CourseSerializer
    lookup_field = "id"


class CourseModulesListAPIView(generics.ListAPIView):
    serializer_class = course_serializer.ModuleSerializer

    @method_decorator(cache_page(60 * 15))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        course_id = self.kwargs["id"]
        course = generics.get_object_or_404(course_models.Course, id=course_id)
        return course_models.Module.objects.filter(course=course).order_by(
            "order"
        )


class ModuleContentsListAPIView(generics.ListAPIView):
    serializer_class = course_serializer.ContentSerializer

    @method_decorator(cache_page(60 * 15))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        module_id = self.kwargs["id"]
        module = generics.get_object_or_404(course_models.Module, id=module_id)
        return course_models.Content.objects.filter(module=module).order_by(
            "order"
        )


class CartAPIView(generics.GenericAPIView):
    permission_classes = IsAuthenticated
    serializer_class = sales_serializer.CartSerializer

    def get(self, request):
        user = request.user
        cart = CoreService.get_user_cart(user)
        serializer = self.serializer_class(cart)
        return Response(serializer.data)


class CartAddAPIView(generics.GenericAPIView):
    permission_classes = IsAuthenticated
    serializer_class = sales_serializer.AddToCartSerializer

    def post(self, request):
        user = request.user
        serializer = sales_serializer.AddToCartSerializer(
            data=request.data, context={"user": user}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartRemoveAPIView(generics.GenericAPIView):
    permission_classes = IsAuthenticated
    serializer_class = sales_serializer.RemoveFromCartSerializer

    def post(self, request):
        user = request.user
        serializer = sales_serializer.RemoveFromCartSerializer(
            data=request.data, context={"user": user}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartClearAPIView(generics.GenericAPIView):
    permission_classes = IsAuthenticated

    def post(self, request):
        user = request.user
        cart = CoreService.get_user_cart(user)
        cart.clear()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ApplyCouponAPIView(generics.GenericAPIView):
    permission_classes = IsAuthenticated
    serializer_class = sales_serializer.ApplyCouponSerializer

    def post(self, request):
        user = request.user
        serializer = self.serializer_class(
            data=request.data, context={"user": user}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateOrderAPIView(generics.GenericAPIView):
    permission_classes = IsAuthenticated
    serializer_class = sales_serializer.CreateOrderSerializer

    def post(self, request):
        user = request.user
        cart = CoreService.get_user_cart(user)
        serializer = self.serializer_class(
            data=request.data, context={"user": user, "cart": cart}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data)


class VerifyTransactionAPIView(generics.GenericAPIView):
    permission_classes = IsAuthenticated
    serializer_class = sales_serializer.VerifyTransactionSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
