from django import forms
from .models import Student

class StudentRegistrationForm(forms.ModelForm):
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
