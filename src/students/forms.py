from django import forms
from django.core.validators import RegexValidator
from .models import Student

class StudentRegistrationForm(forms.ModelForm):
    mobile = forms.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\d{10,15}$',
                message='Phone number must be between 10 and 15 digits.',
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your mobile number (10-15 digits)'
        })
    )

    class Meta:
        model = Student
        fields = ['full_name', 'ref_number', 'email', 'mobile', 'department']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'ref_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your reference number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your mobile number'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
        }
