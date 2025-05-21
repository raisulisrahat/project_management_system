from django.urls import path, re_path
from ctspms.views import ProjectCreateView, ProjectListView, ProjectDetailView, ProjectUpdateView, ProjectDeleteView, TaskCreateView, BacklogView, CalendarView, TaskListView, TaskUpdateView, TaskDeleteView, KanbanBoardView,  TaskDetailView, upload_temp_file, ajax_search, move_to_backlog, mark_notifications_read
urlpatterns = [
    # Project URLs
    path('search/', ajax_search, name='ajax_search'),
    path('projects/', ProjectListView.as_view(), name='projects'),
    path('projects/create/', ProjectCreateView.as_view(), name='project_create'),
    path('projects/<str:label>/summary/', ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<str:label>/tasks/board/', KanbanBoardView.as_view(), name='kanban_board'),
    path('projects/<str:label>/tasks/backlog/', BacklogView.as_view(), name='backlog'),
    path('projects/<str:label>/tasks/create/', TaskCreateView.as_view(), name='task_create'),
    path('projects/<str:label>/tasks/', TaskListView.as_view(), name='task_lists'),
    re_path(r'^projects/(?P<label>[\w\-]+)/tasks/(?P<unique_id>[A-Z]+-\d+)/$', TaskDetailView.as_view(), name='task_detail'),
    re_path(r'^projects/(?P<label>[\w\-]+)/tasks/(?P<unique_id>[A-Z]+-\d+)/edit/$', TaskUpdateView.as_view(), name='task_update'),
    re_path(r'^projects/(?P<label>[\w\-]+)/tasks/(?P<unique_id>[A-Z]+-\d+)/delete/$', TaskDeleteView.as_view(), name='task_delete'),
    path('projects/<str:label>/edit/', ProjectUpdateView.as_view(), name='project_update'),
    path('projects/<str:label>/delete/', ProjectDeleteView.as_view(), name='project_delete'),
    path('upload-temp-file/', upload_temp_file, name='upload_temp_file'),
    path('tasks/move-to-backlog/', move_to_backlog, name='move_to_backlog'),
    path('projects/<str:label>/tasks/calendar/', CalendarView.as_view(), name='calendar_view'),
    path('notifications/mark_read/', mark_notifications_read, name='mark_notifications_read')


]
