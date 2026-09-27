from django import forms
from django.contrib.auth.models import User

class ContactForm(forms.Form):

    name = forms.CharField(
        max_length=100
    )

    email = forms.EmailField()

    phone_number = forms.CharField(
        max_length=20
    )

    message = forms.CharField(
        widget=forms.Textarea
    )


class RegisterForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

    def clean_email(self):

        email = self.cleaned_data["email"]

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email is already registered."
            )

        return email


class LoginForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())