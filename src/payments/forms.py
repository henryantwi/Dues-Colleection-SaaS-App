from django import forms

from .models import Payment


class PaymentForm(forms.ModelForm):
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500",
                "step": "0.01",
                "min": "0",
            }
        ),
    )

    class Meta:
        model = Payment
        fields = ["method", "amount"]
        widgets = {
            "method": forms.Select(
                attrs={
                    "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                }
            ),
        }
