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
BASE_INPUT_CLASS = (
    "peer block w-full p-3 rounded-md border border-gray-300 shadow-sm "
    "focus:border-cyan-500 focus:ring-cyan-500 sm:text-sm bg-white"
)
FLOATING_LABEL_INPUT = (
    "peer block w-full p-3 rounded-md border border-gray-300 shadow-sm "
    "focus:border-cyan-500 focus:ring-cyan-500 sm:text-sm bg-white"
)

SELECT_CLASS = (
    "block w-full p-3 rounded-md border border-gray-300 shadow-sm "
    "focus:border-cyan-500 focus:ring-cyan-500 sm:text-sm bg-white"
)

FILE_INPUT_CLASS = (
    "block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 "
    "file:rounded-md file:border-0 file:bg-cyan-600 file:text-white "
    "hover:file:bg-cyan-700"
)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(required=True, label="First Name")
    last_name = forms.CharField(required=False, label="Last Name")

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize widget attributes
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': BASE_INPUT_CLASS,
                'placeholder': field.label,
                'id': f'id_{field_name}',
                'autocomplete': 'off',
            })

        # Clear default help texts
        for field in ['username', 'password1', 'password2']:
            self.fields[field].help_text = ""

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('profile_image', 'address', 'country', 'department')
        widgets = {
            'profile_image': forms.FileInput(attrs={
                'class': FILE_INPUT_CLASS,
                'type': 'file',
                'id': 'formFile',
                'placeholder': 'Add Profile Image'
            }),
            'address': forms.Textarea(attrs={
                'class': FLOATING_LABEL_INPUT,
                'placeholder': 'Address',
                'rows': 5,
                'id': 'id_address'
            }),
            'country': forms.Select(attrs={
                'class': SELECT_CLASS,
                'placeholder': "Select Country",
                'id': 'id_country'
            }),
            'department': forms.Select(attrs={
                'class': SELECT_CLASS,
                'placeholder': "Select Department",
                'id': 'id_department'
            }),
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
