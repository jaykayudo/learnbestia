# Create your views here.
from rest_framework import generics
from rest_framework.response import Response

from core.models.user import Instructor
from core.utils import CorePagination
from instructor.permissions import IsInstructor
from instructor.services.dashboard import DashboardService
from instructor.services.wallet import WalletService
from instructor.serializers.instructor import (
    WalletTransactionSerializer,
    WithdrawalRequestSerializer,
    WithdrawalRequestCreateSerializer,
)


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


class WalletBalanceAPIView(generics.GenericAPIView):
    permission_classes = [IsInstructor]
    pagination_class = CorePagination

    def get(self, request):
        instructor = Instructor.objects.get(user=request.user)
        balance = WalletService.get_wallet_balance(instructor)
        data = {
            "wallet_balance": balance,
        }
        return Response(data)


class WalletTransactionListAPIView(generics.ListAPIView):
    permission_classes = [IsInstructor]
    serializer_class = WalletTransactionSerializer
    pagination_class = CorePagination

    def get_queryset(self):
        instructor = Instructor.objects.get(user=self.request.user)
        type_param = self.request.query_params.get("type")
        filter_by_type = None
        if type_param is not None and type_param.isdigit():
            filter_by_type = int(type_param)
        transactions = WalletService.get_wallet_transactions(instructor, filter_by_type)
        return transactions.order_by("-created_at")


class WithdrawalRequestListAPIView(generics.ListAPIView):
    permission_classes = [IsInstructor]
    pagination_class = CorePagination
    serializer_class = WithdrawalRequestSerializer

    def get_queryset(self):
        instructor = Instructor.objects.get(user=self.request.user)
        requests = WalletService.get_withdrawal_requests(instructor)
        return requests


class WithdrawalRequestCreateAPIView(generics.GenericAPIView):
    permission_classes = [IsInstructor]
    serializer_class = WithdrawalRequestCreateSerializer

    def post(self, request):
        instructor = Instructor.objects.get(user=request.user)
        wallet = WalletService.get_instructor_wallet(instructor)
        serializer = self.serializer_class(
            data=request.data,
            context={
                "instructor": instructor,
                "wallet": wallet,
            },
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data)
