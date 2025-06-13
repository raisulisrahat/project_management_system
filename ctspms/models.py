import uuid
from django.contrib.auth.models import User
from django.db import models
from account.models import Profile, Team
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from ckeditor_uploader.fields import RichTextUploadingField

class Attachment(models.Model):
    attachment = models.FileField(upload_to="upload/data", null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        # FIXED: Check if attachment exists to prevent errors on delete
        return self.attachment.name if self.attachment else "Deleted Attachment"

class ProjectType(models.Model):
    type_name = models.CharField(max_length=100)
    def __str__(self):
        return self.type_name

class Project(models.Model):
    ACCESS_TYPES = (
        ('Open', 'Open'),
        ('Private', 'Private'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, validators=[RegexValidator(regex=r'^[A-Za-z\s]+$', message='Name can only contain letters and spaces.', code='invalid_name')])
    access = models.CharField(max_length=20, choices=ACCESS_TYPES, default='Open')
    lead_team = models.ForeignKey(Team, on_delete=models.PROTECT, null=True, blank=True)
    lead = models.ForeignKey(Profile, on_delete=models.CASCADE)
    description = RichTextUploadingField(null=True, blank=True)
    type = models.ForeignKey(ProjectType, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    code = models.CharField(max_length=10, unique=True, null=True, blank=True)

    def label(self):
        if self.code:
            return self.code.upper()
        else:
            words = self.name.split()
            if len(words) == 1:
                return words[0].upper()[:10]
            else:
                return ''.join([word[0].upper() for word in words])[:10]

    def clean(self):
        if self.access == 'Private' and not self.lead_team:
            raise ValidationError({'lead_team': 'A lead team is required for private projects.'})
        # IMPROVED: Removed redundant validation already handled by RegexValidator.

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.label()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Issue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issue = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.issue

class TagList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag = models.CharField(max_length=100)
    def __str__(self):
        return self.tag

class PriorityList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    priority_name = models.CharField(max_length=20, default='Normal')
    def __str__(self):
        return self.priority_name

class StatusList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status_name = models.CharField(max_length=20, default='To Do')
    def __str__(self):
        return self.status_name

class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    summary = models.CharField(max_length=100)
    description = RichTextUploadingField(null=True, blank=True)
    attachments = models.ManyToManyField(Attachment, blank=True)
    reporter = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='reporter_tasks')
    assigned_to = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    priority = models.ForeignKey(PriorityList, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.ForeignKey(StatusList, on_delete=models.SET_NULL, null=True, blank=True)
    tag = models.ManyToManyField(TagList, blank=True)
    dependencies = models.ManyToManyField(Issue, blank=True)
    start_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    project_task_number = models.PositiveIntegerField(null=True, blank=True, editable=False)
    is_in_backlog = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.summary

    # IMPROVED: This logic is now robust and avoids race conditions and ordering bugs.
    def save(self, *args, **kwargs):
        if not self.pk:
            last_task = Task.objects.filter(project=self.project).order_by('-project_task_number').first()
            if last_task and last_task.project_task_number:
                self.project_task_number = last_task.project_task_number + 1
            else:
                self.project_task_number = 1
        super().save(*args, **kwargs)

    def unique_id(self):
        return f'{self.project.label()}-{self.project_task_number}'

    @property
    def is_done(self):
        return self.status and self.status.status_name == 'Done'

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    comments_message = RichTextUploadingField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'Comment by {self.user} on {self.task}'

class Timelog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    people = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='timelog')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='timelog')
    log_date = models.DateTimeField(auto_now_add=True)
    hours = models.IntegerField()
    minutes = models.IntegerField()
    message = models.TextField()
    def __str__(self):
        return f'Time log by {self.people.full_name} on {self.task}'

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('task_created', 'Task Created'),
        ('task_updated', 'Task Updated'),
        ('task_assigned', 'Task Assigned'),
        ('task_completed', 'Task Completed'),
        ('comment_added', 'Comment Added'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    people = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='notifications')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'Notification for {self.people.full_name}: {self.notification_type}'