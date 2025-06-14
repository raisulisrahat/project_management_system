# forms.py
from django import forms
from account.models import Invitation
from django.contrib.auth.models import User
from account.models import Profile, Team
from django.contrib.auth.forms import UserCreationForm
from ckeditor_uploader.widgets import CKEditorUploadingWidget


# --- TAILWIND CSS FORM STYLING CONSTANTS ---
SELECT_CLASS = "block w-full p-2.5 rounded-md border-gray-300 shadow-sm focus:border-cyan-500 focus:ring-cyan-500 sm:text-sm"
FILE_INPUT_CLASS = "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-cyan-50 file:text-cyan-700 hover:file:bg-cyan-100"
TEXTAREA_CLASS = "block w-full rounded-md border-gray-300 shadow-sm focus:border-cyan-500 focus:ring-cyan-500 sm:text-sm"
FLOATING_LABEL_INPUT = "block w-100 p-3 rounded-md border-gray-300 shadow-sm focus:border-cyan-500 focus:ring-cyan-500 sm:text-sm"




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
            'username': forms.TextInput(attrs={'class': FLOATING_LABEL_INPUT, 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': FLOATING_LABEL_INPUT, 'id':'exampleInputEmail1', 'type':'email', 'placeholder': 'Email Address'}),
            'first_name': forms.TextInput(attrs={'class': FLOATING_LABEL_INPUT, 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': FLOATING_LABEL_INPUT, 'placeholder': 'Last Name'}),
            'password1': forms.TextInput(attrs={'class': FLOATING_LABEL_INPUT, 'id':'inputPassword3', 'type':'password', 'placeholder': 'Password'}),
            'password2': forms.TextInput(attrs={'class': FLOATING_LABEL_INPUT, 'id':'inputPassword3', 'type':'password', 'placeholder': 'Confirm Password'}),
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
            'profile_image': forms.FileInput(attrs={'class': FILE_INPUT_CLASS, 'type': 'file', 'id':'formFile', 'placeholder': 'AddProfile Image'}),
            'address': forms.Textarea(attrs={'class': FLOATING_LABEL_INPUT, 'placeholder': 'Address', 'rows': 5}),
            'country': forms.Select(attrs={'class': SELECT_CLASS, 'placeholder': "Select Country"}),
            'department': forms.Select(attrs={'class': SELECT_CLASS, 'placeholder': "Select Department"}),
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
            'name': forms.TextInput(attrs={'class': FLOATING_LABEL_INPUT, 'placeholder': 'Name'}),
            'user_id': forms.SelectMultiple(attrs={'class': FLOATING_LABEL_INPUT, 'id':'checkboxSelectMultiple'}),
            'about_info':  CKEditorUploadingWidget(attrs={'cols': 80, 'rows': 10}),
        }
