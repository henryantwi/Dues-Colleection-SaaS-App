from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full p-2 border rounded-md focus:ring-primary focus:border-primary',
            'placeholder': 'Enter your email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full p-2 border rounded-md focus:ring-primary focus:border-primary',
            'placeholder': 'Enter your password'
        })
    )

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, username=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    'Please enter a correct email and password. Note that both fields may be case-sensitive.',
                    code='invalid_login'
                )
        return self.cleaned_data
