from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Ticket(models.Model):
    class Category(models.TextChoices):
        FACILITY = 'facility', _('Facility / Equipment')
        CLEANING = 'cleaning', _('Cleaning')
        ELECTRICAL = 'electrical', _('Electrical')
        PLUMBING = 'plumbing', _('Plumbing')
        INTERNET = 'internet', _('Internet / Network')
        SECURITY = 'security', _('Security')
        OTHER = 'other', _('Other')

    class Priority(models.TextChoices):
        LOW = 'low', _('Low')
        MEDIUM = 'medium', _('Medium')
        HIGH = 'high', _('High')
        URGENT = 'urgent', _('Urgent')

    class Status(models.TextChoices):
        OPEN = 'open', _('Open')
        IN_PROGRESS = 'in_progress', _('In Progress')
        RESOLVED = 'resolved', _('Resolved')
        CLOSED = 'closed', _('Closed')

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name=_('Student')
    )
    room = models.ForeignKey(
        'dormitory.Room',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        verbose_name=_('Room')
    )
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    description = models.TextField(verbose_name=_('Description'))
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
        verbose_name=_('Category')
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name=_('Priority')
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name=_('Status')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        verbose_name=_('Assigned To')
    )

    class Meta:
        verbose_name = _('Ticket')
        verbose_name_plural = _('Tickets')
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.pk} - {self.title} ({self.get_status_display()})"


class TicketReply(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='replies',
        verbose_name=_('Ticket')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ticket_replies',
        verbose_name=_('User')
    )
    message = models.TextField(verbose_name=_('Message'))
    is_internal = models.BooleanField(
        default=False,
        verbose_name=_('Internal Note (Admin only)')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    class Meta:
        verbose_name = _('Ticket Reply')
        verbose_name_plural = _('Ticket Replies')
        ordering = ['created_at']

    def __str__(self):
        return f"Reply to #{self.ticket_id} by {self.user}"
