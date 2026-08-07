from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Ticket, TicketReply


class TicketCreateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('title', 'description', 'category', 'priority')
        labels = {
            'title': _('Title'),
            'description': _('Description'),
            'category': _('Category'),
            'priority': _('Priority'),
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }


class TicketReplyForm(forms.ModelForm):
    class Meta:
        model = TicketReply
        fields = ('message',)
        labels = {'message': _('Your Reply')}
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Write your reply...')}),
        }


class AdminTicketReplyForm(forms.ModelForm):
    class Meta:
        model = TicketReply
        fields = ('message', 'is_internal')
        labels = {
            'message': _('Reply'),
            'is_internal': _('Internal note (only visible to admins)'),
        }
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AdminTicketStatusForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('status', 'priority', 'assigned_to')
        labels = {
            'status': _('Status'),
            'priority': _('Priority'),
            'assigned_to': _('Assign To'),
        }
