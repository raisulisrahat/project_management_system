# forms.py
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from ctspms.models import Comment, Project, Task

class ProjectForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget(attrs={'cols': 80, 'rows': 10}))

    class Meta:
        model = Project
        fields = ('name', 'lead', 'description', 'code', 'type')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Name'}),
            'type': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Project Type'}),
            'lead': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Project Level'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Code'}),
        }
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
        widgets = {
            'description': CKEditorUploadingWidget(),
        }


class CommentForm(forms.ModelForm):
    comments_message = forms.CharField(widget=CKEditorUploadingWidget(attrs={'cols': 80, 'rows': 10}))

    class Meta:
        model = Comment
        fields = ['comments_message']
