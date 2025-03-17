from django.urls import path
from ctspms.views import ProjectCreateView, TaskCreateView, ProjectListView, TaskListView, KanbanBoardView, ProjectDetailView, TaskDetailView, ajax_search

urlpatterns = [
    # Project URLs
    path('search/', ajax_search, name='ajax_search'),
    path('projects/', ProjectListView.as_view(), name='projects'),
    path('projects/<str:label>/summary/', ProjectDetailView.as_view(), name='project_detail'),
    path('projects/create/', ProjectCreateView.as_view(), name='project_create'),
    # path('projects/<str:label>/edit/', ProjectUpdateView.as_view(), name='project_edit'),
    # # Task URLs
    path('tasks/board/', KanbanBoardView.as_view(), name='kanban_board'),
    path('projects/<str:lable>/list/', TaskListView.as_view(), name='list'),
    # Correct URL pattern
    path('projects/<str:label>/boards/<str:unique_id>/', TaskDetailView.as_view(), name='task_detail'),
    path('projects/<str:label>/tasks/create/', TaskCreateView.as_view(), name='task_create'),
    # path('tasks/<str:uniqe_id>/edit/', TaskUpdateView.as_view(), name='task_edit'),

]
