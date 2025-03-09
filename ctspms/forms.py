# forms.py
from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comments_message', 'attachment']  # Add attachment field here

    attachment = forms.FileField(required=False)  # Make attachment optional
