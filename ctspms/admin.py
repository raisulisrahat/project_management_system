from django.contrib import admin
from ctspms.models import Project, ProjectType, Task, Comment, Attachment, Timelog,  Notification, TagList, StatusList, PriorityList, Issue



@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('label', 'name', 'lead', 'type')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('unique_id', 'priority', 'status', 'reporter', 'assigned_to')

@admin.register(Timelog)
class TimelogAdmin(admin.ModelAdmin):
    list_display = ('people','task', 'hours', 'log_date', )



@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'comment')

admin.site.register(Attachment)
admin.site.register(TagList)
admin.site.register(StatusList)
admin.site.register(PriorityList)
admin.site.register(Issue)
admin.site.register(ProjectType)
