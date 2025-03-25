# forms.py
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.contrib.admin.widgets import AdminDateWidget

from ctspms.models import Comment, Project, Task

class ProjectForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget(attrs={'cols': 80, 'rows': 10}))

    class Meta:
        model = Project
        fields = ('name', 'description', 'code', 'type', 'access', 'lead_team')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'type': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Type'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Key'}),
            'access': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Access'}),
            'lead_team': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Team Member'}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('summary', 'description', 'reporter', 'assigned_to', 'status', 'dependencies', 'priority', 'due_date')

        widgets = {
            'summary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task Summary'}),
            'description': CKEditorUploadingWidget(attrs={'cols': 80, 'rows': 10}),
            'status': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Task Status'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Assignee'}),
            # Correct field name
            'reporter': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Reporter'}),
            'dependencies': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Dependencies'}),
            'priority': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Priority'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            # Use 'type': 'date' for HTML5 datepicker
        }
        project = forms.ModelChoiceField(queryset=Project.objects.all(), widget=forms.HiddenInput())


class CommentForm(forms.ModelForm):
    comments_message = forms.CharField(widget=CKEditorUploadingWidget(attrs={'cols': 80, 'rows': 10}))

    class Meta:
        model = Comment
        fields = ['comments_message']


class ProjectSelectForm(forms.Form):
    project = forms.ModelChoiceField(queryset=Project.objects.all(), label="Select Project", widget=forms.Select(attrs={'class': 'form-control'}))