# forms.py
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.contrib.admin.widgets import AdminDateWidget
from ctspms.models import Comment, Project, Task, StatusList

class ProjectForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget(attrs={'cols': 80, 'rows': 10}), required=False)

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


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput(attrs={'class': 'custom-file-input', 'multiple': True}))  # Explicitly set multiple attribute
        super(MultipleFileField, self).__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if not data:
            return initial
        # Handle multiple file inputs
        if isinstance(data, (list, tuple)):
            # Clean each file in the list
            return [super(MultipleFileField, self).clean(d, initial) for d in data]
        return super(MultipleFileField, self).clean(data, initial)


class TaskForm(forms.ModelForm):
    attachments = MultipleFileField(required=False)

    class Meta:
        model = Task
        fields = (
        'summary', 'description', 'reporter', 'attachments', 'assigned_to', 'status', 'dependencies', 'priority',
        'due_date')

        widgets = {
            'summary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task Summary'}),
            'description': CKEditorUploadingWidget(attrs={'cols': 80, 'rows': 10}),
            'status': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Task Status'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Assignee'}),
            'reporter': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Reporter'}),
            'dependencies': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Dependencies'}),
            'priority': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Priority'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class CommentForm(forms.ModelForm):
    comments_message = forms.CharField(widget=CKEditorUploadingWidget(attrs={'cols': 80, 'rows': 10}))

    class Meta:
        model = Comment
        fields = ['comments_message']


class ProjectSelectForm(forms.Form):
    project = forms.ModelChoiceField(queryset=Project.objects.all(), label="Select Project", widget=forms.Select(attrs={'class': 'form-control'}))