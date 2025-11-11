from decimal import Decimal
from core.models.user import (
    Instructor,
    InstructorWallet,
    WalletTransaction,
    WalletTransactionType,
    WithdrawalRequest,
)


class WalletService:
    @classmethod
    def get_instructor_wallet(cls, instructor: Instructor) -> InstructorWallet:
        wallet, _ = InstructorWallet.objects.get_or_create(instructor=instructor)
        return wallet

    @classmethod
    def get_wallet_balance(cls, instructor: Instructor) -> Decimal:
        wallet = InstructorWallet.objects.get(instructor=instructor)
        return wallet.amount

    @classmethod
    def get_wallet_transactions(
        cls,
        instructor: Instructor,
        filter_by_type: WalletTransactionType | int | None = None,
    ):
        wallet = cls.get_instructor_wallet(instructor)
        transactions = WalletTransaction.objects.filter(wallet=wallet)
        if filter_by_type is not None:
            transactions = transactions.filter(type=filter_by_type)
        return transactions

    @classmethod
    def get_withdrawal_requests(cls, instructor: Instructor):
        requests = WithdrawalRequest.objects.filter(instructor=instructor)
        return requests.order_by("-created_at")
