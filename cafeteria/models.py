from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta


class MealType(models.Model):
    name_fa = models.CharField(max_length=50, verbose_name=_('Name (Persian)'))
    name_en = models.CharField(max_length=50, verbose_name=_('Name (English)'))
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name=_('Price (Toman)'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))

    class Meta:
        verbose_name = _('Meal Type')
        verbose_name_plural = _('Meal Types')

    def __str__(self):
        return self.name_fa

    def get_name(self, lang='fa'):
        return self.name_fa if lang == 'fa' else self.name_en


class WeeklyMenu(models.Model):
    class DayOfWeek(models.IntegerChoices):
        SATURDAY = 0, _('Saturday')
        SUNDAY = 1, _('Sunday')
        MONDAY = 2, _('Monday')
        TUESDAY = 3, _('Tuesday')
        WEDNESDAY = 4, _('Wednesday')
        THURSDAY = 5, _('Thursday')
        FRIDAY = 6, _('Friday')

    class MealTime(models.TextChoices):
        BREAKFAST = 'breakfast', _('Breakfast')
        LUNCH = 'lunch', _('Lunch')
        DINNER = 'dinner', _('Dinner')

    week_start = models.DateField(verbose_name=_('Week Start Date'))
    day = models.IntegerField(choices=DayOfWeek.choices, verbose_name=_('Day'))
    meal_time = models.CharField(max_length=20, choices=MealTime.choices, verbose_name=_('Meal Time'))
    meal_type = models.ForeignKey(
        MealType,
        on_delete=models.CASCADE,
        related_name='menus',
        verbose_name=_('Meal')
    )
    description = models.TextField(blank=True, verbose_name=_('Description'))
    is_available = models.BooleanField(default=True, verbose_name=_('Available'))

    class Meta:
        verbose_name = _('Weekly Menu')
        verbose_name_plural = _('Weekly Menus')
        unique_together = ['week_start', 'day', 'meal_time']
        ordering = ['week_start', 'day', 'meal_time']

    def __str__(self):
        return f"{self.get_day_display()} - {self.get_meal_time_display()} - {self.meal_type}"


class FoodOrder(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        CONFIRMED = 'confirmed', _('Confirmed')
        CANCELLED = 'cancelled', _('Cancelled')
        SERVED = 'served', _('Served')

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='food_orders',
        verbose_name=_('Student')
    )
    menu_item = models.ForeignKey(
        WeeklyMenu,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('Menu Item')
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_('Status')
    )
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name=_('Price'))
    ordered_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Ordered At'))
    notes = models.TextField(blank=True, verbose_name=_('Notes'))

    class Meta:
        verbose_name = _('Food Order')
        verbose_name_plural = _('Food Orders')
        ordering = ['-ordered_at']

    def __str__(self):
        return f"{self.student} - {self.menu_item} ({self.get_status_display()})"


class Transaction(models.Model):
    class Type(models.TextChoices):
        DEPOSIT = 'deposit', _('Deposit')
        WITHDRAW = 'withdraw', _('Withdraw / Food Order')
        REFUND = 'refund', _('Refund')
        ADJUSTMENT = 'adjustment', _('Admin Adjustment')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_('User')
    )
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_('Amount'))
    type = models.CharField(max_length=20, choices=Type.choices, verbose_name=_('Type'))
    description = models.CharField(max_length=255, blank=True, verbose_name=_('Description'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_transactions',
        verbose_name=_('Created By')
    )

    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.amount} ({self.get_type_display()})"
