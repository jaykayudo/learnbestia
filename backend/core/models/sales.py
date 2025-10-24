# module for models that have to do with course purchases
import secrets
from decimal import Decimal
from functools import cached_property

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db import transaction as db_transaction
from django.utils import timezone

from .base import BaseModel
from .course import Course, CourseStudent
from .user import User


class OrderStatus(models.IntegerChoices):
    NEW = 0, "New"
    PAID = 1, "Paid"


class Coupon(BaseModel):
    """
    courses - if there are courses in the courses field,
        then the coupon should be for the courses included else
        the coupon is for all courses.

    uses: if uses is a number, it can be used that number of times
        if uses is None, it can be used infinitely till it expires.
    """

    code = models.CharField(max_length=20)
    discount = models.PositiveIntegerField(
        validators=[MaxValueValidator(100), MinValueValidator(0)]
    )
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    courses = models.ManyToManyField(Course, blank=True)
    uses = models.PositiveIntegerField(default=1, null=True, blank=True)

    def __str__(self) -> str:
        return self.code

    @property
    def is_valid(self):
        now = timezone.now()
        if now > self.valid_from and now < self.valid_to:
            if self.uses is None or self.uses > 0:
                return True
        return False

    def redeem_coupon(self):
        if self.is_valid:
            if self.uses:
                self.uses -= 1
            return True
        return False

    def discount_price(self, price: Decimal):
        discount = Decimal(self.discount / 100) * price
        return price - discount


class Cart(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def total_price(self):
        return self.cartitem_set.all()

    @property
    def is_empty(self):
        return self.cartitem_set.count() == 0

    def revalidate_coupon(self):
        if self.coupon:
            if not self.coupon.is_valid:
                self.coupon = None
                self.save()

    def clear(self):
        self.cartitem_set.all().delete()


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    @property
    def price(self):
        return self.course.price

    @cached_property
    def discounted_price(self):
        if not self.cart.coupon:
            return self.course.price
        if not self.cart.coupon.is_valid:
            return self.course.price
        if coupon_courses := self.cart.coupon.courses.all():
            if self.course in coupon_courses:
                return self.cart.coupon.discount_price(self.course.price)
            return self.course.price
        return self.cart.coupon.discount_price(self.course.price)


class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ref = models.CharField(max_length=20, editable=False, unique=True)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.IntegerField(choices=OrderStatus.choices, default=OrderStatus.NEW)

    @property
    def total_price(self):
        return OrderItem.objects.filter(order=self).aggregate(
            total_price=models.Sum("price")
        )["total_price"]

    def save(self, *args, **kwargs) -> None:
        while not self.ref:
            ref = secrets.token_urlsafe(18)
            if not Order.objects.filter(ref=ref).exists():
                self.ref = ref
        return super().save(*args, **kwargs)

    @db_transaction.atomic
    def create_order(self):
        cart: Cart = self.user.cart
        cart_items = CartItem.objects.filter(cart=cart)
        for item in cart_items:
            OrderItem.objects.create(order=self, course=item.course)
        # clear cart after order creation and revalidate cart coupon
        cart.revalidate_coupon()
        cart.clear()

    def tx_verify(self):
        # TODO: send mail to user with receipt asynchronously
        self.status = OrderStatus.PAID
        self.save()
        for item in self.orderitem_set.all():
            CourseStudent.objects.create(course=item.course, user=self.user)


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=15, decimal_places=2)

    def calculate_price(self):
        if not self.order.coupon:
            return self.course.price
        if not self.order.coupon.is_valid:
            return self.course.price
        if coupon_courses := self.order.coupon.courses.all():
            if self.course in coupon_courses:
                self.order.coupon.redeem_coupon()  # redeem the coupon
                return self.order.coupon.discount_price(self.course.price)
            return self.course.price
        self.order.coupon.redeem_coupon()  # redeem the coupon
        return self.order.coupon.discount_price(self.course.price)

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.calculate_price()
        return super().save(*args, **kwargs)
