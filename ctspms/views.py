from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView, CreateView, ListView, DetailView, UpdateView, DeleteView
from ctspms.models import StatusList, TagList, PriorityList, Issue, Project, Task, Comment, Attachment, Timelog, Notification
from account.models import Department, Role



@require_GET
def ajax_search(request):
    query = request.GET.get('q', '')  # Get the query from the GET request
    results = {}  # To store all results

    if query:  # Only search if query is not empty

        # 1. Search for projects
        project_queryset = Project.objects.filter(name__icontains=query)
        project_results = [{'label': project.label, 'title': project.title} for project in project_queryset]
        results['projects'] = project_results

        # 2. Search for tasks
        task_queryset = Task.objects.filter(task_name__icontains=query)
        task_results = [{'summary': task.summery, 'unique_id': task.unique_id()} for task in task_queryset]
        results['tasks'] = task_results

        # 3. Search for issues
        issue_queryset = Issue.objects.filter(issue__icontains=query)
        issue_results = [{'title': issue.issue} for issue in issue_queryset]
        results['issues'] = issue_results

        # 4. Search for teams (departments)
        department_queryset = Department.objects.filter(department_name__icontains=query)
        department_results = [{'department_name': department.department_name} for department in department_queryset]
        results['departments'] = department_results

        return JsonResponse({'results': results})
    return JsonResponse({'error': 'No query provided'}, status=400)

# Create Views
class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'projects/project_form.html'
    fields = ['name', 'description', 'start_date', 'type', 'lead', 'end_date']  # Include necessary fields
    success_url = reverse_lazy('project_list')  # Redirect to project list after creating

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'tasks/task_form.html'
    fields = ['summery', 'description', 'status', 'assigned_to', 'reporter', 'due_date', 'project', 'priority', 'tag']  # Include necessary fields
    success_url = reverse_lazy('task_create')  # Redirect to task list after creating

class StatusCreateView(LoginRequiredMixin, CreateView):
    model = StatusList
    template_name = 'tasks/task_form.html'  # Add the correct template path
    fields = ['status_name']  # Include necessary fields
    success_url = reverse_lazy('task_create')  # Redirect to task list after creating

# List Views
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'  # Context variable in the template

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/board.html'
    context_object_name = 'tasks'  # Context variable in the template

# Detail View
class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'  # Context variable for the template

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

