from django.urls import path
from ctspms.views import ProjectCreateView, ProjectListView, ProjectDetailView, ProjectUpdateView, ProjectDeleteView, TaskCreateView, BacklogView, TaskListView, TaskUpdateView, TaskDeleteView, KanbanBoardView,  TaskDetailView, upload_temp_file, ajax_search
urlpatterns = [
    # Project URLs
    path('search/', ajax_search, name='ajax_search'),
    path('projects/', ProjectListView.as_view(), name='projects'),
    path('projects/create/', ProjectCreateView.as_view(), name='project_create'),
    path('projects/<str:label>/summary/', ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<str:label>/board/', KanbanBoardView.as_view(), name='kanban_board'),
    path('projects/<str:label>/backlog/', BacklogView.as_view(), name='backlog'),
    path('projects/<str:label>/lists/', TaskListView.as_view(), name='task_lists'),
    path('projects/<str:label>/boards/<str:unique_id>/', TaskDetailView.as_view(), name='task_detail'),
    path('projects/<str:label>/tasks/create/', TaskCreateView.as_view(), name='task_create'),
    path('projects/<str:label>/tasks/<str:unique_id>/edit/', TaskUpdateView.as_view(), name='task_update'),
    path('projects/<str:label>/tasks/<str:unique_id>/delete/', TaskDeleteView.as_view(), name='task_delete'),
    path('projects/<str:label>/edit/', ProjectUpdateView.as_view(), name='project_update'),
    path('projects/<str:label>/delete/', ProjectDeleteView.as_view(), name='project_delete'),
    path('upload-temp-file/', upload_temp_file, name='upload_temp_file'),
    # path('tasks/<str:uniqe_id>/edit/', TaskUpdateView.as_view(), name='task_edit'),

]
