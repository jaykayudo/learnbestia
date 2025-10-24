from django.db import transaction as db_transaction
from models import course as course_models
from models import sales
from models import user as user_models
from rest_framework import generics, serializers

from core import exceptions
from core.service import CoreService

from . import course as course_serializer


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = sales.Coupon
        fields = ["code", "discount", "is_valid"]


class CartItemSerializer(serializers.ModelSerializer):
    course = course_serializer.SimpleCourseSerializer()

    class Meta:
        model = sales.CartItem
        fields = ["course", "price", "discounted_price"]


class CartSerializer(serializers.ModelSerializer):
    coupon = CouponSerializer()
    items = serializers.SerializerMethodField()

    class Meta:
        model = sales.Cart
        fields = "__all__"

    def get_items(self, obj: sales.Cart):
        items = CoreService.get_cart_contents(obj)
        data = CartItemSerializer(items, many=True).data
        return data


class AddToCartSerializer(serializers.Serializer):
    course = serializers.UUIDField()

    def validate(self, attrs):
        course = generics.get_object_or_404(course_models.Course, id=attrs["course"])
        self.context["course"] = course
        return attrs

    @db_transaction.atomic
    def save(self):
        course = self.context["course"]
        CoreService.add_to_cart(self.context["user"], course)


class RemoveFromCartSerializer(serializers.Serializer):
    course = serializers.UUIDField()

    def validate(self, attrs):
        course = generics.get_object_or_404(course_models.Course, id=attrs["course"])
        self.context["course"] = course
        return attrs

    @db_transaction.atomic
    def save(self):
        course = self.context["course"]
        CoreService.remove_from_cart(self.context["user"], course)


class ApplyCouponSerializer(serializers.Serializer):
    coupon = serializers.CharField()

    def validate(self, attrs):
        coupon = generics.get_object_or_404(sales.Coupon, code=attrs["coupon"])
        if not coupon.is_valid:
            raise exceptions.CouponIsInvalid
        self.context["coupon"] = coupon
        return attrs

    def save(self):
        coupon = self.context["coupon"]
        CoreService.apply_coupon(self.context["user"], coupon)


class CreateOrderSerializer(serializers.Serializer):
    """
    context:
        - user
        - cart
    """

    payment_method = serializers.ChoiceField(
        user_models.Transaction.PAYMENT_METHODS.choices
    )

    def validate(self, attrs):
        cart: sales.Cart = self.context["cart"]
        user = self.context["user"]
        items = sales.CartItem.objects.filter(cart=cart)
        for item in items:
            if user in item.course.students.all():
                raise serializers.ValidationError(
                    {"detail": f"{item.course} already Purchased"}
                )
        return attrs

    def save(self):
        order, tx = CoreService.create_order(
            self.context["user"], self.validated_data["payment_method"]
        )
        return {
            "ref": tx.ref,
            "order": order.id_str,
            "payment_method": tx.payment_method,
        }


class VerifyTransactionSerializer(serializers.Serializer):
    transaction = serializers.CharField()

    def validate(self, attrs):
        try:
            transaction = user_models.Transaction.objects.get(ref=attrs["transaction"])
        except user_models.Transaction.DoesNotExist:
            raise exceptions.InvalidTransaction
        if transaction.status != transaction.STATUSES.INITAILIZED:
            raise exceptions.InvalidTransaction
        self.context["transaction"] = transaction
        return attrs

    def save(self):
        CoreService.verify_transaction(self.context["transaction"])
