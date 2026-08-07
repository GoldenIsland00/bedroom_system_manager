from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Building(models.Model):
    class Section(models.TextChoices):
        BROTHERS = 'brothers', _('Brothers Section')
        SISTERS = 'sisters', _('Sisters Section')

    name = models.CharField(max_length=100, verbose_name=_('Building Name'))
    section = models.CharField(
        max_length=20,
        choices=Section.choices,
        verbose_name=_('Section')
    )
    floors = models.PositiveIntegerField(default=1, verbose_name=_('Number of Floors'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))

    class Meta:
        verbose_name = _('Building')
        verbose_name_plural = _('Buildings')
        ordering = ['section', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_section_display()})"


class Room(models.Model):
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name='rooms',
        verbose_name=_('Building')
    )
    number = models.CharField(max_length=20, verbose_name=_('Room Number'))
    floor = models.PositiveIntegerField(default=1, verbose_name=_('Floor'))
    capacity = models.PositiveIntegerField(default=4, verbose_name=_('Capacity'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    description = models.TextField(blank=True, verbose_name=_('Description'))

    class Meta:
        verbose_name = _('Room')
        verbose_name_plural = _('Rooms')
        unique_together = ['building', 'number']
        ordering = ['building', 'floor', 'number']

    def __str__(self):
        return f"{self.building.name} - {self.number}"

    @property
    def occupied_beds(self):
        return self.beds.filter(is_occupied=True).count()

    @property
    def available_beds(self):
        return self.capacity - self.occupied_beds


class Bed(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='beds',
        verbose_name=_('Room')
    )
    bed_number = models.PositiveIntegerField(verbose_name=_('Bed Number'))
    is_occupied = models.BooleanField(default=False, verbose_name=_('Occupied'))
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bed',
        verbose_name=_('Student')
    )

    class Meta:
        verbose_name = _('Bed')
        verbose_name_plural = _('Beds')
        unique_together = ['room', 'bed_number']
        ordering = ['room', 'bed_number']

    def __str__(self):
        status = _('Occupied') if self.is_occupied else _('Empty')
        return f"{self.room} - Bed {self.bed_number} ({status})"

    def assign_student(self, student):
        if self.is_occupied:
            raise ValueError(_('Bed is already occupied'))
        self.student = student
        self.is_occupied = True
        self.save()

    def release(self):
        self.student = None
        self.is_occupied = False
        self.save()
