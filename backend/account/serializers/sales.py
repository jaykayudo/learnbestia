from rest_framework import serializers

from core.models import sales

from . import course as course_serializer


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = sales.Coupon
        fields = ["code", "discount", "is_valid"]


class OrderItemSerializer(serializers.ModelSerializer):
    course = course_serializer.SimpleCourseSerializer()

    class Meta:
        model = sales.OrderItem
        fields = ["course", "price"]


class OrderSerializer(serializers.ModelSerializer):
    coupon = CouponSerializer()
    items = serializers.SerializerMethodField()

    class Meta:
        model = sales.Order
        fields = ["ref", "coupon", "status", "created_at", "items"]

    def get_items(self, obj):
        items = obj.orderitem_set.all()
        data = OrderItemSerializer(items, many=True).data
        return data
