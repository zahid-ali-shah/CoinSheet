import uuid
import datetime
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class Item(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_deprecated = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class DailyExpense(TimeStampedModel):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name='daily_expenses', help_text="Item of daily expense"
    )
    transaction = models.OneToOneField('PaymentTransaction', on_delete=models.RESTRICT)
    is_loan = models.BooleanField(default=False, help_text="Whether this expense is a loan")

    @staticmethod
    def get_all_expenses(user, month, year):
        return DailyExpense.objects.filter(
            transaction__user=user, transaction__date__month=month, transaction__date__year=year,
        ).select_related(
            'item', 'transaction', 'transaction__payment_mode', 'transaction__user',
        ).all().order_by('transaction__date', 'transaction__payment_mode__type')

    @staticmethod
    def get_sum_of_expenses(user, month, year):
        return DailyExpense.objects.filter(
            transaction__user=user, transaction__date__month=month, transaction__date__year=year,
        ).select_related('transaction__user', 'item', 'transaction', 'transaction__payment_mode').aggregate(
            Sum('transaction__amount', default=0)
        )['transaction__amount__sum']

    def __str__(self):
        return f'{self.item}'


class TypeOfPaymentModes(models.TextChoices):
    CASH = "CA", _("Cash")
    CREDIT = "CR", _("Credit Card")
    BANK = "BN", _("Bank transaction")


class PaymentMode(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=2, choices=TypeOfPaymentModes, default=TypeOfPaymentModes.CASH)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_active = models.BooleanField(default=True)
    bg_color = models.CharField(max_length=6, default='175175')

    def __str__(self):
        return f'{self.name}'


class PaymentTransaction(TimeStampedModel):
    payment_mode = models.ForeignKey(PaymentMode, on_delete=models.RESTRICT, related_name='transactions')
    date = models.DateField(default=datetime.date.today)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_transactions'
    )
    is_deposited = models.BooleanField(default=False)
    comment = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.is_deposited:
            self.amount = -self.amount
        super().save(*args, **kwargs)

    @staticmethod
    def get_all(user, month, year, mode):
        return PaymentTransaction.objects.filter(
            user=user, date__month=month, date__year=year, payment_mode=mode
        ).select_related(
            'user', 'payment_mode'
        ).all().order_by('date', 'created')

    @staticmethod
    def get_all_name(user, month, year, mode):
        return PaymentTransaction.objects.filter(
            user=user, date__month=month, date__year=year, payment_mode=mode
        ).select_related(
            'user', 'payment_mode'
        ).all().order_by('date', 'created')

    @staticmethod
    def get_sum(user, month, year, mode):
        return PaymentTransaction.get_all(user, month, year, mode).aggregate(
            Sum('amount', default=0)
        )['amount__sum']

    @staticmethod
    def get_queryset_sum(transactions):
        return transactions.aggregate(
            Sum('amount', default=0)
        )['amount__sum']

    @staticmethod
    def get_ob(user, month, year, mode):
        from core.helpers import get_pre_month
        month, year = get_pre_month(month, year)
        return PaymentTransaction.objects.filter(
            user=user, date__month__lte=month, date__year__lte=year, payment_mode=mode
        ).select_related(
            'user', 'payment_mode'
        ).all().aggregate(Sum('amount', default=0))['amount__sum']

    def __str__(self):
        return f'{self.id} - {self.amount}'
