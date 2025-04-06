from django import forms
from account.models import Invitation
from django.contrib.auth.models import User
from account.models import Profile, Team
from django.contrib.auth.forms import UserCreationForm
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        labels = {
            'username': '',
            'email': '',
            'first_name': '',
            'last_name': '',
            'password1': '',
            'password2': '',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'id':'exampleInputEmail1', 'type':'email', 'placeholder': 'Email Address'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'password1': forms.TextInput(attrs={'class': 'form-control', 'id':'inputPassword3', 'type':'password', 'placeholder': 'Password'}),
            'password2': forms.TextInput(attrs={'class': 'form-control', 'id':'inputPassword3', 'type':'password', 'placeholder': 'Confirm Password'}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('profile_image', 'address', 'country', 'department')
        widgets = {
            'profile_image': forms.FileInput(attrs={'class': 'form-control', 'type': 'file', 'id':'formFile', 'placeholder': 'AddProfile Image'}),
            'address': forms.Textarea(attrs={'class': "form-control", 'placeholder': 'Address', 'rows': 5}),
            'country': forms.Select(attrs={'class': "form-control", 'placeholder': "Select Country"}),
            'department': forms.Select(attrs={'class': "form-control", 'placeholder': "Select Department"}),
        }


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

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team

        fields = ('name', 'user_id', 'about_info')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'user_id': forms.SelectMultiple(attrs={'class': 'form-control', 'id':'checkboxSelectMultiple'}),
            'about_info':  CKEditorUploadingWidget(attrs={'cols': 80, 'rows': 10}),
        }
