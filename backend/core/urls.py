from django.urls import path

from . import views

urlpatterns = [
    path(
        "categories/",
        views.CourseCategoryListAPIView.as_view(),
        name="categories",
    ),
    path("courses/", views.CourseListAPIView.as_view(), name="courses"),
    path(
        "courses/<uuid:id>/",
        views.CourseDetailAPIView.as_view(),
        name="course_details",
    ),
    path(
        "courses/<uuid:id>/modules/",
        views.CourseModulesListAPIView.as_view(),
        name="course_modules",
    ),
    path(
        "modules/<uuid:id>/contents/",
        views.ModuleContentsListAPIView.as_view(),
        name="module_contents",
    ),
    path("cart/", views.CartAPIView.as_view(), name="cart"),
    path("cart/add/", views.CartAddAPIView.as_view(), name="cart_add"),
    path(
        "cart/remove/", views.CartRemoveAPIView.as_view(), name="cart_remove"
    ),
    path("cart/clear/", views.CartClearAPIView.as_view(), name="cart_clear"),
    path(
        "create-order/",
        views.CreateOrderAPIView.as_view(),
        name="create_order",
    ),
    path(
        "verify-transaction/",
        views.VerifyTransactionAPIView.as_view(),
        name="verify_transaction",
    ),
]
