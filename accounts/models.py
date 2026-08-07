from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', _('Student')
        ADMIN = 'admin', _('Admin')
        STAFF = 'staff', _('Staff')

    class Gender(models.TextChoices):
        MALE = 'male', _('Male / Brother')
        FEMALE = 'female', _('Female / Sister')

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name=_('Role')
    )
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        blank=True,
        null=True,
        verbose_name=_('Gender')
    )
    student_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_('Student ID')
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name=_('Phone')
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name=_('Balance (Toman)')
    )
    national_id = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_('National ID')
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name=_('Avatar')
    )
    is_active_student = models.BooleanField(
        default=True,
        verbose_name=_('Active Student')
    )

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.student_id or '-'})"

    @property
    def is_admin_user(self):
        return self.role in [self.Role.ADMIN, self.Role.STAFF] or self.is_superuser

    @property
    def full_name(self):
        return self.get_full_name() or self.username
