# forms.py
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from ctspms.models import Comment

class CommentForm(forms.ModelForm):
    comments_message = forms.CharField(widget=CKEditorUploadingWidget(attrs={'cols': 10, 'rows': 10}))

    class Meta:
        model = Comment
        fields = ['comments_message']
