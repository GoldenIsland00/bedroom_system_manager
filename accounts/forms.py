from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_('Username / Student ID'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Username or Student ID'),
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Password'),
            'autocomplete': 'current-password',
        })
    )


class StudentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label=_('First Name'), max_length=30, required=True)
    last_name = forms.CharField(label=_('Last Name'), max_length=30, required=True)
    student_id = forms.CharField(label=_('Student ID'), max_length=20, required=True)
    gender = forms.ChoiceField(label=_('Gender'), choices=User.Gender.choices)
    phone = forms.CharField(label=_('Phone'), max_length=15, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'student_id', 'gender', 'phone', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone', 'avatar')
        labels = {
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'phone': _('Phone'),
            'avatar': _('Avatar'),
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
