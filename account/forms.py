from django import forms
from account.models import Invitation
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        labels = {'email': 'Email',}

class InvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ['email']  # Only the email field

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField()


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6, label='OTP')
    new_password = forms.CharField(widget=forms.PasswordInput, label='New Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
