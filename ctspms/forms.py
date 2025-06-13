from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Comment, Project, Task

# --- TAILWIND CSS FORM STYLING CONSTANTS ---
TEXT_INPUT_CLASS = "block w-100 p-3 rounded-md border-gray-300 shadow-sm focus:border-cyan-500 focus:ring-cyan-500 sm:text-sm"
SELECT_CLASS = "block w-100 p-3 rounded-md border-gray-300 shadow-sm focus:border-cyan-500 focus:ring-cyan-500 sm:text-sm"
TEXTAREA_CLASS = "block w-full rounded-md border-gray-300 shadow-sm focus:border-cyan-500 focus:ring-cyan-500 sm:text-sm"
FILE_INPUT_CLASS = "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-cyan-50 file:text-cyan-700 hover:file:bg-cyan-100"


class ProjectSelectForm(forms.Form):
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        label="Select Project",
        widget=forms.Select(attrs={'class': SELECT_CLASS})
    )

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'code', 'type', 'access', 'lead_team']
        widgets = {
            'name': forms.TextInput(attrs={'class': TEXT_INPUT_CLASS, 'placeholder': 'e.g., New Website Development'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 4}),
            'code': forms.TextInput(attrs={'class': TEXT_INPUT_CLASS, 'placeholder': 'e.g., WEB, APP, MKT'}),
            'type': forms.Select(attrs={'class': SELECT_CLASS}),
            'access': forms.Select(attrs={'class': SELECT_CLASS}),
            'lead_team': forms.SelectMultiple(attrs={'class': SELECT_CLASS}),
        }

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput(attrs={'class': 'hidden'})) # The widget is hidden and triggered by a custom label
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if not data:
            return initial
        if isinstance(data, (list, tuple)):
            return [super().clean(d, initial) for d in data]
        return super().clean(data, initial)

class TaskForm(forms.ModelForm):
    attachments = MultipleFileField(required=False)

    class Meta:
        model = Task
        fields = ('summary', 'description', 'reporter', 'attachments', 'assigned_to', 'status', 'dependencies', 'priority', 'due_date')
        widgets = {
            'summary': forms.TextInput(attrs={'class': TEXT_INPUT_CLASS, 'placeholder': 'Enter a concise task summary...'}),
            'description': CKEditorUploadingWidget(),
            'status': forms.Select(attrs={'class': SELECT_CLASS}),
            'assigned_to': forms.Select(attrs={'class': SELECT_CLASS}),
            'reporter': forms.Select(attrs={'class': SELECT_CLASS}),
            'dependencies': forms.Select(attrs={'class': SELECT_CLASS}),
            'priority': forms.Select(attrs={'class': SELECT_CLASS}),
            'due_date': forms.DateInput(attrs={'class': TEXT_INPUT_CLASS, 'type': 'date'}),
        }

class CommentForm(forms.ModelForm):
    comments_message = forms.CharField(widget=CKEditorUploadingWidget())
    class Meta:
        model = Comment
        fields = ['comments_message']

# class ProjectForm(forms.ModelForm):
#     description = forms.CharField(widget=CKEditorUploadingWidget(attrs={'cols': 80, 'rows': 10}), required=False)
#
#     class Meta:
#         model = Project
#         fields = ('name', 'description', 'code', 'type', 'access', 'lead_team', 'end_date')
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
#             'type': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Type'}),
#             'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Key'}),
#             'access': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Access'}),
#             'lead_team': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Team Member'}),
#             # 'start_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Start Date'}),
#             'end_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'End Date'}),
#         }


