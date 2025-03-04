import uuid
from django.contrib.auth.models import User
from django.db import models
from account.models import Profile
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

class ProjectType(models.Model):
    type_name = models.CharField(max_length=100)
    def __str__(self):
        return self.type_name

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

class StatusList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status_name = models.CharField(max_length=20, default='To Do')

    def __str__(self):
        return self.status_name

class PriorityList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    priority_name = models.CharField(max_length=20, default='Normal')

    def __str__(self):
        return self.priority_name

class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, validators=[RegexValidator(regex=r'^[A-Za-z\s]+$', message='Name can only contain letters and spaces.', code='invalid_name')])
    lead = models.ForeignKey(Profile, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    type = models.ForeignKey(ProjectType, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    code = models.CharField(max_length=10, unique=True, null=True, blank=True)  # Unique project code field

    def label(self):
        if self.code:  # If project code exists, use it
            return self.code.upper()
        else:
            words = self.name.split()
            if len(words) == 1:
                return words[0].upper()
            else:
                return ''.join([word[0].upper() for word in words])

    def clean(self):
        if not self.name.replace(' ', '').isalpha():
            raise ValidationError('Name can only contain letters and spaces.')

    def __str__(self):
        return self.name



class Task(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically increments for each task
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    summary = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    reporter = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reporter_tasks')
    assigned_to = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='assigned_tasks')
    priority = models.ForeignKey(PriorityList, on_delete=models.CASCADE)
    status = models.ForeignKey(StatusList, on_delete=models.SET_NULL, null=True, blank=True)
    tag = models.ManyToManyField(TagList, blank=True)
    dependencies = models.ManyToManyField(Issue, blank=True)
    start_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)

    project_task_number = models.PositiveIntegerField(null=True, blank=True)  # Task number within project

    def __str__(self):
        return self.summary

    def save(self, *args, **kwargs):
        # Automatically set project-specific task number if not already set
        if not self.project_task_number:
            # Find the last task for the project, ordered by project_task_number
            last_task = Task.objects.filter(project=self.project).order_by('-id').first()

            # If a last task exists, increment its project_task_number, else start at 1
            if last_task:
                self.project_task_number = last_task.project_task_number + 1
            else:
                self.project_task_number = 1

        super(Task, self).save(*args, **kwargs)  # Call the real save() method

    def unique_id(self):
        # Use the project's label (HMS, PMS, etc.) and the project_task_number
        return f'{self.project.label()}-{self.project_task_number}'
class Attachment(models.Model):
    file_path = models.FileField(upload_to="upload/data")  # Use FileField for uploaded files
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='attachments')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='documents')

    def __str__(self):
        return self.file_path.name

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField(null=True, blank=True)
    attachment = models.ForeignKey(Attachment, on_delete=models.CASCADE)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.note



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
    NOTIFICATION_TYPES  = (
        ('task_created', 'Task Created'),
        ('task_updated', 'Task Updated'),
        ('task_assigned', 'Task Assigned'),
        ('task_completed', 'Task Completed'),
        ('comment_added', 'Comment Added'),
        ('task_due', 'Task Due Soon'),
        ('project_updated', 'Project Updated'),
        ('task_mentioned', 'Task Mentioned'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    people = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='notifications')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='notifications')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notifications')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='notifications')
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Return a readable description based on the type of notification
        if self.notification_type == 'task_assigned':
            return f'{self.people.full_name()} assigned to Task: {self.task.summary}'
        elif self.notification_type == 'comment_added':
            return f'New comment added on Task: {self.task.summary}'
        elif self.notification_type == 'task_updated':
            return f'Task {self.task.summary} updated'
        elif self.notification_type == 'task_due':
            return f'Task {self.task.summary} is due soon'
        elif self.notification_type == 'project_updated':
            return f'Project {self.project.name} updated'
        else:
            return f'Notification: {self.notification_type}'

    def mark_as_read(self):
        """Method to mark the notification as read"""
        self.read = True
        self.save()

    def mark_as_unread(self):
        """Method to mark the notification as unread"""
        self.read = False
        self.save()

