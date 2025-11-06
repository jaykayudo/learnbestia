from decimal import Decimal

from django.db.models import Count, Sum

from core.models.user import (
    Instructor,
    WalletTransaction,
    InstructorWallet,
    WalletTransactionType,
)
from core.models.course import Course


class DashboardService:
    @classmethod
    def get_number_of_students(cls, instructor: Instructor) -> int:
        # get all instructor course
        courses = Course.objects.filter(instructor=instructor)
        # get distint students using aggregate and count and return
        data = courses.aaggregate(number_of_students=Count("students", distinct=True))
        return data["number_of_students"]

    @classmethod
    def get_number_of_courses(cls, instructor: Instructor) -> int:
        # get all instructor course
        courses = Course.objects.filter(instructor=instructor)
        return courses.count()

    @classmethod
    def get_total_earnings(cls, instructor: Instructor) -> Decimal:
        wallet = InstructorWallet.objects.get(instructor=instructor)
        wallet_transactions = WalletTransaction.objects.filter(
            wallet=wallet, transaction_type=WalletTransactionType.CREDIT
        )
        data = wallet_transactions.aggregate(total_earning=Sum("amount"))
        return data["total_earnings"]
