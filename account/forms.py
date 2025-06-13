# forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Invitation, Profile, Team

# --- TAILWIND CSS FORM STYLING CONSTANTS ---
SELECT_CLASS = "block w-full p-2.5 rounded-md border-gray-300 shadow-sm focus:border-cyan-500 focus:ring-cyan-500 sm:text-sm"
FILE_INPUT_CLASS = "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-cyan-50 file:text-cyan-700 hover:file:bg-cyan-100"
TEXTAREA_CLASS = "block w-full rounded-md border-gray-300 shadow-sm focus:border-cyan-500 focus:ring-cyan-500 sm:text-sm"
FLOATING_LABEL_INPUT = "peer block w-full appearance-none rounded-md border px-3 py-3 text-gray-900 placeholder-transparent focus:outline-none sm:text-sm"

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Enter a valid email.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css = FLOATING_LABEL_INPUT
            if self.errors.get(field_name):
                css += ' border-red-500 ring-red-500 focus:border-red-500 focus:ring-red-500'
            else:
                css += ' border-gray-300 focus:border-cyan-500 focus:ring-cyan-500'

            autocomplete_map = {
                'first_name': 'given-name',
                'last_name': 'family-name',
                'email': 'email',
                'username': 'username',
                'password1': 'new-password',
                'password2': 'new-password',
            }

            field.widget.attrs.update({
                'class': css,
                'placeholder': ' ',
                'autocomplete': autocomplete_map.get(field_name, 'off'),
            })

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('profile_image', 'address', 'country', 'department')
        widgets = {
            'profile_image': forms.FileInput(attrs={'class': FILE_INPUT_CLASS}),
            'address': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 4}),
            'country': forms.Select(attrs={'class': SELECT_CLASS}),
            'department': forms.Select(attrs={'class': SELECT_CLASS}),
        }

class InvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': FLOATING_LABEL_INPUT + ' border-gray-300 focus:border-cyan-500 focus:ring-cyan-500', 'placeholder': ' '})
        }

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': FLOATING_LABEL_INPUT + ' border-gray-300 focus:border-cyan-500 focus:ring-cyan-500', 'placeholder': ' '}))

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'class': FLOATING_LABEL_INPUT + ' border-gray-300 focus:border-cyan-500 focus:ring-cyan-500', 'placeholder': ' '}))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': FLOATING_LABEL_INPUT + ' border-gray-300 focus:border-cyan-500 focus:ring-cyan-500', 'placeholder': ' '}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': FLOATING_LABEL_INPUT + ' border-gray-300 focus:border-cyan-500 focus:ring-cyan-500', 'placeholder': ' '}))

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
            'name': forms.TextInput(attrs={'class': FLOATING_LABEL_INPUT + ' border-gray-300 focus:border-cyan-500 focus:ring-cyan-500', 'placeholder': ' '}),
            'user_id': forms.SelectMultiple(attrs={'class': SELECT_CLASS}),
            'about_info': CKEditorUploadingWidget(),
        }
