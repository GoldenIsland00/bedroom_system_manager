from django import forms
from django.utils.translation import gettext_lazy as _
from .models import FoodOrder, WeeklyMenu


class FoodOrderForm(forms.Form):
    menu_items = forms.ModelMultipleChoiceField(
        queryset=WeeklyMenu.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_('Select Meals')
    )

    def __init__(self, *args, week_start=None, **kwargs):
        super().__init__(*args, **kwargs)
        if week_start:
            self.fields['menu_items'].queryset = WeeklyMenu.objects.filter(
                week_start=week_start,
                is_available=True
            ).select_related('meal_type')
