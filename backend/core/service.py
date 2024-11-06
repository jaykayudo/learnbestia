from django.contrib.contenttypes.models import ContentType
from models import course as course_models
from models import sales as sales_models
from models import user as user_models
from rest_framework.exceptions import ValidationError

from . import exceptions


class DashboardService:
    pass


class CoreService:
    @classmethod
    def get_user_cart(cls, user: user_models.User) -> sales_models.Cart:
        return user.cart

    @classmethod
    def get_course_reviews(cls, course: course_models.Course):
        reviews = course_models.CourseReview.objects.filter(
            course=course
        ).order_by("-created_at")
        return reviews

    @classmethod
    def get_module_contents(cls, module: course_models.Module):
        contents = course_models.Content.objects.filter(module=module)
        return contents

    @classmethod
    def get_course_modules(cls, course: course_models.Course):
        modules = course_models.Module.objects.filter(course=course)
        return modules.order_by("order")

    @classmethod
    def get_cart_contents(cls, cart: sales_models.Cart):
        cartitems = sales_models.CartItem.objects.filter(cart=cart)
        return cartitems

    @classmethod
    def apply_coupon(cls, user: user_models.User, coupon: sales_models.Coupon):
        if not coupon.is_valid:
            return  # raise error here later
        cart: sales_models.Cart = cls.get_user_cart(user)
        cart.coupon = coupon
        cart.save()

    @classmethod
    def remove_coupon(cls, user: user_models.User):
        cart: sales_models.Cart = cls.get_user_cart(user)
        cart.coupon = None
        cart.save()

    @classmethod
    def add_to_cart(cls, user: user_models.User, course: course_models.Course):
        cart: sales_models.Cart = cls.get_user_cart(user)
        item, _ = sales_models.CartItem.objects.get_or_create(
            cart=cart, course=course
        )
        return item

    @classmethod
    def remove_from_cart(
        cls, user: user_models.User, course: sales_models.Course
    ):
        cart: sales_models.Cart = cls.get_user_cart(user)
        sales_models.CartItem.objects.filter(cart=cart, course=course).delete()

    @classmethod
    def create_order(
        cls,
        user: user_models.User,
        payment_method: user_models.Transaction.PAYMENT_METHODS,
    ):
        cart: sales_models.Cart = cls.get_user_cart(user)
        if cart.is_empty:
            raise exceptions.CartIsEmpty

        order = sales_models.Order.objects.create(
            user=user, coupon=cart.coupon
        )
        order.create_order()
        order_ct = ContentType.objects.get_for_model(sales_models.Order)
        tx = user_models.Transaction.objects.create(
            item_ct=order_ct,
            item_id=order.id,
            amount=order.total_price,
            payment_method=payment_method,
            reason=user_models.Transaction.REASONS.ORDER_PAY,
        )
        return order, tx

    @classmethod
    def verify_transaction(cls, tx: user_models.Transaction):
        try:
            tx.verify()
        except Exception as err:
            raise ValidationError({"detail": str(err)})
