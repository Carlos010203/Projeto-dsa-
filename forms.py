from django import forms
from .models import Category


class TransactionForm(forms.Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    description = forms.CharField(max_length=255, required=False)
