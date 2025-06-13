import json, os, uuid
from django.db import models
from django.db.models import Count
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .models import StatusList, Project, Task, Comment, Attachment
from account.models import Profile
from chat.models import Meeting
from .forms import CommentForm, TaskForm, ProjectForm


# ----------------- AJAX/UTILITY VIEWS -----------------

@require_POST
@login_required
def mark_notifications_read(request):
    request.user.profile.notifications.filter(read=False).update(read=True)
    return JsonResponse({'status': 'success'})


@require_GET
@login_required
def ajax_search(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'error': 'No query provided'}, status=400)

    project_queryset = Project.objects.filter(name__icontains=query)[:5]
    task_queryset = Task.objects.filter(summary__icontains=query).select_related('project')[:5]

    results = {
        'projects': [{'label': p.label(), 'title': p.name, 'url': reverse('project_detail', args=[p.code])} for p in project_queryset],
        'tasks': [{'summary': t.summary, 'unique_id': t.unique_id(),
                   'url': reverse('task_detail', args=[t.project.code, t.unique_id()])} for t in task_queryset],
    }
    return JsonResponse({'results': results})


@csrf_exempt
@require_POST
@login_required
def move_to_backlog(request):
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        task = Task.objects.get(id=task_id)
        task.is_in_backlog = not task.is_in_backlog
        task.save()
        return JsonResponse({'success': True, 'in_backlog': task.is_in_backlog})
    except (json.JSONDecodeError, Task.DoesNotExist, KeyError):
        return JsonResponse({'success': False, 'error': 'Invalid task ID or malformed request'}, status=400)


@csrf_exempt
@require_POST
@login_required
def upload_temp_file(request):
    if not request.FILES.get('file'):
        return JsonResponse({'success': False, 'error': 'No file provided'}, status=400)

    uploaded_file = request.FILES['file']
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_uploads')
    os.makedirs(temp_dir, exist_ok=True)

    file_name = f"{uuid.uuid4()}_{uploaded_file.name}"
    file_path = os.path.join(temp_dir, file_name)
    file_path_saved = default_storage.save(file_path, ContentFile(uploaded_file.read()))

    return JsonResponse({'success': True, 'file_path': file_path_saved})


# ----------------- PROJECT VIEWS -----------------

class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10
    ordering = ['-start_date']


class ProjectCreateView(LoginRequiredMixin, CreateView):
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('projects')

    def form_valid(self, form):
        project = form.save(commit=False)
        project.lead = self.request.user.profile
        project.save()
        messages.success(self.request, f"Project '{project.name}' created successfully.")
        return super().form_valid(form)


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/summary.html'
    context_object_name = 'project'

    def get_object(self, queryset=None):
        return get_object_or_404(Project, code__iexact=self.kwargs['label'].upper())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object

        status_data = project.tasks.values('status__status_name').annotate(count=Count('id')).order_by()
        context['task_statuses'] = [item['status__status_name'] for item in status_data if item['status__status_name']]
        context['task_counts'] = [item['count'] for item in status_data if item['status__status_name']]

        priority_data = project.tasks.values('priority__priority_name').annotate(count=Count('id')).order_by()
        context['task_priorities'] = [item['priority__priority_name'] for item in priority_data if item['priority__priority_name']]
        context['task_priority_counts'] = [item['count'] for item in priority_data if item['priority__priority_name']]

        total_tasks = project.tasks.count()
        if total_tasks > 0:
            workload_data = project.tasks.exclude(assigned_to=None).values('assigned_to__user__first_name').annotate(task_count=Count('id'))
            context['unique_assigned_users'] = [item['assigned_to__user__first_name'] for item in workload_data]
            context['user_task_percentages'] = [(item['task_count'] / total_tasks) * 100 for item in workload_data]

        return context


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form_modify.html'
    slug_field = 'code'
    slug_url_kwarg = 'label'

    def get_success_url(self):
        messages.success(self.request, "Project details updated.")
        return reverse_lazy('project_detail', kwargs={'label': self.object.code})


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects')
    slug_field = 'code'
    slug_url_kwarg = 'label'

    def form_valid(self, form):
        messages.success(self.request, f"Project '{self.object.name}' has been deleted.")
        return super().form_valid(form)


# ----------------- TASK VIEWS -----------------

class TaskListView(LoginRequiredMixin, ListView):
    template_name = 'tasks/tasks.html'
    context_object_name = 'tasks'
    paginate_by = 10

    def get_queryset(self):
        self.project = get_object_or_404(Project, code=self.kwargs['label'].upper())
        return Task.objects.filter(project=self.project).order_by('-start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    form_class = TaskForm
    template_name = 'tasks/task_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, code=self.kwargs['label'].upper())
        return context

    def form_valid(self, form):
        task = form.save(commit=False)
        task.project = get_object_or_404(Project, code=self.kwargs['label'].upper())
        task.reporter = self.request.user.profile
        if not task.status:
            task.status, _ = StatusList.objects.get_or_create(status_name='To Do')
        task.save()

        files = self.request.FILES.getlist('attachments')
        for file in files:
            task.attachments.create(attachment=file)

        messages.success(self.request, f"Task '{task.summary}' created successfully.")
        return redirect('task_lists', label=task.project.code)


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'tasks/task_detail.html'

    def get_object(self, queryset=None):
        project = get_object_or_404(Project, code=self.kwargs['label'].upper())
        task_number = self.kwargs.get('unique_id').split('-')[-1]
        return get_object_or_404(Task, project=project, project_task_number=task_number)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.object.project
        context['comment_form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            messages.success(request, "Your comment has been posted.")
        return redirect('task_detail', label=task.project.code, unique_id=task.unique_id())


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form_modify.html'
    context_object_name = 'task'

    def get_object(self, queryset=None):
        project = get_object_or_404(Project, code=self.kwargs['label'].upper())
        task_number = self.kwargs.get('unique_id').split('-')[-1]
        return get_object_or_404(Task, project=project, project_task_number=task_number)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.object.project
        return context

    def get_success_url(self):
        messages.success(self.request, f"Task '{self.object.summary}' has been updated.")
        return reverse('task_detail', args=[self.object.project.code, self.object.unique_id()])


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    context_object_name = 'task'

    def get_object(self, queryset=None):
        project = get_object_or_404(Project, code=self.kwargs['label'].upper())
        task_number = self.kwargs.get('unique_id').split('-')[-1]
        return get_object_or_404(Task, project=project, project_task_number=task_number)

    def get_success_url(self):
        return reverse_lazy('task_lists', args=[self.object.project.code])

    def form_valid(self, form):
        messages.success(self.request, f"Task '{self.object.summary}' has been deleted.")
        return super().form_valid(form)


class KanbanBoardView(LoginRequiredMixin, View):
    template_name = 'tasks/board.html'

    def get(self, request, *args, **kwargs):
        project = get_object_or_404(Project, code=self.kwargs['label'].upper())
        statuses = StatusList.objects.prefetch_related(
            models.Prefetch(
                'task_set',
                queryset=Task.objects.filter(project=project).order_by('id'),
                to_attr='tasks_in_status'
            )
        )
        context = {'project': project, 'statuses': statuses}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            task_id = data.get('task_id')
            new_status_id = data.get('new_status_id')
            task = Task.objects.get(id=task_id)
            task.status_id = new_status_id
            task.save()
            return JsonResponse({'success': True})
        except (json.JSONDecodeError, Task.DoesNotExist, KeyError) as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


class CalendarView(LoginRequiredMixin, View):
    template_name = 'tasks/calendar.html'

    def get(self, request, *args, **kwargs):
        project = get_object_or_404(Project, code=self.kwargs['label'].upper())
        tasks = Task.objects.filter(project=project)
        meetings = Meeting.objects.filter(attendees=request.user.profile)

        events = []
        for task in tasks.iterator():
            if task.due_date:
                events.append({
                    'id': f'task-{task.id}',
                    'title': task.summary,
                    'start': task.start_date.isoformat(),
                    'end': task.due_date.isoformat(),
                    'backgroundColor': '#357edd',
                    'borderColor': '#357edd',
                    'extendedProps': {'url': reverse('task_detail', args=[task.project.code, task.unique_id()])}
                })

        for meeting in meetings.iterator():
            events.append({
                'id': f'meeting-{meeting.id}',
                'title': meeting.title,
                'start': meeting.start_time.isoformat(),
                'end': meeting.end_time.isoformat(),
                'backgroundColor': '#fa8c16',
                'borderColor': '#fa8c16',
                'extendedProps': {'url': reverse('meeting_detail', args=[meeting.pk])}
            })

        context = {
            'project': project,
            'events': json.dumps(events)
        }
        return render(request, self.template_name, context)


class BacklogView(LoginRequiredMixin, View):
    template_name = 'tasks/backlog.html'

    def get(self, request, *args, **kwargs):
        project = get_object_or_404(Project, code=self.kwargs['label'].upper())
        backlog_tasks = Task.objects.filter(project=project, is_in_backlog=True).order_by('priority')
        context = {'project': project, 'tasks': backlog_tasks}
        return render(request, self.template_name, context)
