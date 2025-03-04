from django.http import JsonResponse,Http404
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
        project_results = [{'label': project.label, 'title': project.name} for project in project_queryset]
        results['projects'] = project_results

        # 2. Search for tasks
        task_queryset = Task.objects.filter(task_name__icontains=query)
        task_results = [{'summary': task.summary, 'unique_id': task.unique_id()} for task in task_queryset]
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
    template_name = 'projects/summery.html'
    context_object_name = 'project'

    def get_object(self):
        label = self.kwargs.get('label')
        project = Project.objects.filter(code__iexact=label).first()

        if not project:
            projects = Project.objects.all()
            for proj in projects:
                if proj.label() == label:
                    project = proj
                    break

        if not project:
            raise Http404("Project does not exist")

        return project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Task status breakdown for doughnut chart
        task_statuses = context['project'].tasks.values_list('status__status_name', flat=True).distinct()
        task_counts = [context['project'].tasks.filter(status__status_name=status).count() for status in task_statuses]

        # Task priority breakdown for bar chart
        task_priorities = context['project'].tasks.values_list('priority__priority_name', flat=True).distinct()
        task_priority_counts = [context['project'].tasks.filter(priority__priority_name=priority).count() for priority
                                in task_priorities]

        # Generate a list of unique assigned users for the team workload section
        assigned_users = set()
        user_task_count = {}  # To store task count per user

        for task in context['project'].tasks.all():
            assigned_users.add(task.assigned_to)
            user_task_count[task.assigned_to] = user_task_count.get(task.assigned_to, 0) + 1

        # Calculate total tasks and percentage for each user
        total_tasks = context['project'].tasks.count()
        user_task_percentages = {user: (count / total_tasks) * 100 for user, count in user_task_count.items()}

        # Create a list of tuples (user, percentage) instead of a dictionary
        user_task_percentages_list = [(user, user_task_percentages.get(user, 0)) for user in assigned_users]

        # Pass data to the template
        context['unique_assigned_users'] = list(assigned_users)
        context['user_task_percentages'] = user_task_percentages_list  # Pass as list of tuples

        # Pass chart data to template context
        context['task_statuses'] = list(task_statuses)
        context['task_counts'] = task_counts
        context['task_priorities'] = list(task_priorities)
        context['task_priority_counts'] = task_priority_counts

        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

