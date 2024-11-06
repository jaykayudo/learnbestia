import secrets
import string
from decimal import Decimal

from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.db import models
from django.db import transaction as db_transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from .base import BaseModel, BaseNotification


class AuthProviders(models.TextChoices):
    GOOGLE = "google", "Google"
    EMAIL = "email", "Email"
    ETHEREUM = "Ethereum", "Ethereum"
    POLKADOT = "Polkadot", "Polkadot"


class OTPReasons(models.TextChoices):
    EMAIL_VERIFICATION = "email_verification", "Email Verification"
    PASSWORD_RESET = "password_reset", "Password Reset"


class WalletTransactionType(models.IntegerChoices):
    CREDIT = 1, "Credit"
    DEBIT = 0, "Debit"


class TransactionStatus(models.IntegerChoices):
    INITAILIZED = 0, "Initialized"
    PENDING = 1, "Pending"
    VERIFIED = 2, "Verified"
    FAILED = 3, "Failed"


class TransactionReason(models.TextChoices):
    ORDER_PAY = "order_pay", "Order Pay"
    WALLET_TRANSFER = "wallet_transfer", "Wallet Transfer"
    COURSE_PAYMENT = "course_payment", "Course Payment"


class PaymentMethods(models.TextChoices):
    FIAT = "fiat", "Fiat"
    ERC_USDT = "erc_usdt", "ERC_USDT"
    ERC_USDC = "erc_usdc", "ERC_USDC"
    DOT = "dot", "DOT"
    BESTIA_COIN = "bestia_coin", "BESTIA_COIN"
    INTERNAL = "internal", "Internal"


class WalletTransactionStatus(models.IntegerChoices):
    PENDING = 0, "Pending"
    SUCCESS = 1, "Success"
    FAILED = 2, "Failed"


class BaseManager(UserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault(
            "first_name", "Admin " + str(secrets.token_urlsafe(8))
        )
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(BaseModel, AbstractUser):
    PROVIDERS = AuthProviders

    username = None
    wallet_id = models.TextField(
        _("Wallet Id"), blank=True, null=True, unique=True
    )
    email = models.EmailField(
        _("Email"), max_length=150, unique=True, blank=True, null=True
    )
    first_name = models.CharField(
        _("Last Name"),
        max_length=200,
        help_text=_("Required. Your first name needs to be entered"),
    )
    last_name = models.CharField(_("Last Name"), max_length=200, blank=True)
    is_instructor = models.BooleanField(default=False)
    auth_provider = models.CharField(
        max_length=20,
        choices=AuthProviders.choices,
        default=AuthProviders.EMAIL,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = BaseManager()

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(wallet_id__isnull=False)
                | models.Q(email_isnull=False),
                name="address_or_email_not_null",
            )
        ]

    def __str__(self):
        return self.get_full_name()


class Instructor(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    title = models.CharField(_("Title"), max_length=120)
    bio = models.TextField()
    is_verified = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name()


class OTPManager(models.Manager):
    def create(self, **kwargs):
        model = self.model(**kwargs)
        code = model.set_code()
        model.save(using=self._db)
        return code, model


class OTPToken(BaseModel):
    OTP_REASONS = OTPReasons
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(
        _("Reason"), choices=OTPReasons.choices, max_length=20
    )
    code = models.TextField(_("Code"))
    objects = OTPManager()

    @property
    def get_expiry_time(self):
        return timezone.timedelta(minutes=10)

    def set_code(self):
        code = get_random_string(6, string.digits)
        encoded_code = TimestampSigner().sign(code)
        self.code = encoded_code
        return code

    def verify_code(self, code: str):
        try:
            decoded_code = TimestampSigner().unsign(
                self.code, max_age=self.get_expiry_time
            )
            return code == decoded_code
        except (BadSignature, SignatureExpired):
            return False


class InstructorWallet(BaseModel):
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00")
    )
    is_active = models.BooleanField(default=True)

    @db_transaction.atomic
    def add_balance(self, amount: str | int | float):
        self.amount = models.F("amount") + Decimal(amount)
        self.save()

    @db_transaction.atomic
    def substract_balance(self, amount: str | int | float):
        self.amount = models.F("amount") - Decimal(amount)
        self.save()

    def has_balance(self, amount: str | int | float):
        return self.amount >= Decimal(amount)


class WalletTransaction(BaseModel):
    TYPES = WalletTransactionType
    wallet = models.ForeignKey(InstructorWallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.IntegerField(choices=WalletTransactionType.choices)
    status = models.IntegerField(
        choices=WalletTransactionStatus.choices,
        default=WalletTransactionStatus.PENDING,
    )

    @db_transaction.atomic
    def tx_verify(self):
        if self.status == WalletTransactionStatus.PENDING:
            self.status = WalletTransactionStatus.SUCCESS
            self.save()
            self.wallet.add_balance(self.amount)


class Transaction(BaseModel):
    STATUSES = TransactionStatus
    REASONS = TransactionReason
    PAYMENT_METHODS = PaymentMethods

    item_ct = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=["order", "wallettransaction"],
    )
    item_id = models.UUIDField()
    item = GenericForeignKey("item_ct", "item_id")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    ref = models.CharField(editable=False, max_length=20, unique=True)
    status = models.PositiveIntegerField(
        default=TransactionStatus.INITAILIZED,
        choices=TransactionStatus.choices,
    )
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethods.choices
    )
    reason = models.CharField(max_length=20, choices=TransactionReason.choices)
    date_verified = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        while not self.ref:
            ref = secrets.token_urlsafe(18)
            if not Transaction.objects.filter(ref=ref).exists():
                self.ref = ref
        super().save(*args, **kwargs)

    def verify(self):
        self.item.tx_verify()


class Notification(BaseNotification):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class BulkNotification(BaseNotification):
    users = models.ManyToManyField(User)
