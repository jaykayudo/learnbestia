from django.db import transaction as db_transaction
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from core.models.user import (
    WalletTransaction,
    WithdrawalRequest,
    Coins,
    CryptoWithdrawalInfo,
    FiatWithdrawalInfo,
)


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = "__all__"


class CryptoWithdrawalInfoSerializer(serializers.Serializer):
    coin_type = serializers.ChoiceField(choices=Coins.choices)
    wallet_address = serializers.CharField()


class FiatWithdrawalInfoSerializer(serializers.Serializer):
    bank_name = serializers.CharField()
    account_number = serializers.CharField()
    account_name = serializers.CharField()


class InfoRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, CryptoWithdrawalInfo):
            return CryptoWithdrawalInfoSerializer(value).data
        elif isinstance(value, FiatWithdrawalInfo):
            return FiatWithdrawalInfoSerializer(value).data
        else:
            return str(value)


class WithdrawalRequestSerializer(serializers.ModelSerializer):
    info = InfoRelatedField(read_only=True)

    class Meta:
        model = WithdrawalRequest
        fields = "__all__"


class WithdrawalRequestCreateSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["crypto", "fiat"])
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    info = serializers.DictField()

    def validate(self, attrs):
        amount = attrs["amount"]
        if amount <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        wallet = self.context["wallet"]
        if amount > wallet.amount:
            raise serializers.ValidationError("Insufficient wallet balance.")

        if attrs["type"] == "crypto":
            info_serializer = CryptoWithdrawalInfoSerializer(data=attrs["info"])
        else:
            info_serializer = FiatWithdrawalInfoSerializer(data=attrs["info"])
        info_serializer.is_valid(raise_exception=True)
        info_data = info_serializer.validated_data
        self.context["info_data"] = info_data
        return attrs

    @db_transaction.atomic
    def save(self):
        instrutor = self.context["instructor"]
        amount = self.validated_data["amount"]
        info_data = self.context["info_data"]
        if self.validated_data["type"] == "crypto":
            info = CryptoWithdrawalInfo.objects.create(**info_data)
        else:
            info = FiatWithdrawalInfo.objects.create(**info_data)
        request = WithdrawalRequest.objects.create(
            instructor=instrutor,
            amount=amount,
            payment_type=self.validated_data["type"],
            info_id=info.id,
            info_ct=ContentType.objects.get_for_model(info),
        )
        data = WithdrawalRequestSerializer(request).data
        return data
