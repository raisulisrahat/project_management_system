import os, uuid
from django.views import View
from django.http import JsonResponse,Http404, HttpResponseForbidden
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView, CreateView, ListView, DetailView, UpdateView, DeleteView
from ctspms.models import StatusList, TagList, PriorityList, Issue, Project, Task, Comment, Attachment, Timelog
from account.models import Department, Role, User, Profile
from .forms import CommentForm, TaskForm, ProjectForm, ProjectSelectForm
from django.db import IntegrityError
from django.contrib import messages
from shutil import move

class KanbanBoardView(View):
    model = Task
    template_name = 'tasks/board.html'
    success_url = reverse_lazy('kanban_board')

    def get(self, request):
        tasks = Task.objects.all()
        status = StatusList.objects.all()
        issues = Issue.objects.all()


@csrf_exempt
def upload_temp_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']

        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        os.makedirs(temp_dir, exist_ok=True)

        file_name = f"{uuid.uuid4()}_{uploaded_file.name}"
        file_path = os.path.join(temp_dir, file_name)

        default_storage.save(file_path, ContentFile(uploaded_file.read()))

        return JsonResponse({'success': True, 'file_path': file_path})

    return JsonResponse({'success': False, 'error': 'Invalid request'})
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
class ProjectCreateView(LoginRequiredMixin, View):
    model = Project
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('projects')  # Redirect to project list after creating

    def get(self, request, *args, **kwargs):
        project_form = ProjectForm()
        return render(request, self.template_name, {'form': project_form})

    def post(self, request, *args, **kwargs):
        project_form = ProjectForm(request.POST)
        if project_form.is_valid():
            project = project_form.save(commit=False)
            try:
                project.lead = request.user.profile  # Set the logged-in user as the project lead
                project.save()
            except Profile.DoesNotExist:
                messages.error(request, 'Your profile is missing. Please contact the administrator.')
                return redirect('profile')
            except IntegrityError as e:
                # Catch any integrity errors related to database constraints
                print(f"Database Error: {e}")
                messages.error(request, 'There was an issue saving the project. Please try again.')
                return redirect('project_create')  # Or handle the error appropriately

            return redirect(self.success_url)

        else:
            print(project_form.errors)  # Print form errors in the console for debugging

        return render(request, self.template_name, {'form': project_form})


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        self.object = form.save()

        # Move temp files to the final attachment directory
        temp_files = self.request.POST.getlist('temp_files', [])
        for temp_file_path in temp_files:
            file_name = os.path.basename(temp_file_path)
            final_path = os.path.join(settings.MEDIA_ROOT, 'tasks', file_name)

            move(temp_file_path, final_path)  # Move file

            attachment = Attachment(attachment=final_path)
            attachment.save()
            self.object.attachments.add(attachment)

        return super().form_valid(form)
    def get_success_url(self, project):
        return reverse_lazy('task_lists', kwargs={'label': project.label()})

    def get(self, request, *args, **kwargs):
        label = kwargs.get('label')
        if not label:
            return redirect('projects')

        project = get_object_or_404(Project, code=label)
        task_form = TaskForm()
        return render(request, self.template_name, {'task_form': task_form, 'project': project})

    def post(self, request, *args, **kwargs):
        label = kwargs.get('label')
        if not label:
            return redirect('projects')

        project = get_object_or_404(Project, code=label)
        task_form = TaskForm(request.POST, request.FILES)

        if task_form.is_valid():
            task = task_form.save(commit=False)
            task.project = project

            if request.user.is_authenticated:
                task.reporter = request.user.profile
                if 'assign_me' in request.POST:
                    task.assigned_to = request.user.profile
                else:
                    task.assigned_to = task_form.cleaned_data['assigned_to']

            task.save()  # Save the task to assign it an ID

            # Process and save multiple attachments
            files = request.FILES.getlist('attachments')
            for file in files:
                attachment = Attachment(attachment=file)
                attachment.save()
                task.attachments.add(attachment)  # Add the attachment to the task

            return redirect(self.get_success_url(project))

        return render(request, self.template_name, {'task_form': task_form, 'project': project})


class StatusCreateView(LoginRequiredMixin, CreateView):
    model = StatusList
    template_name = 'tasks/board.html'  # Add the correct template path
    fields = ['status_name']  # Include necessary fields
    success_url = reverse_lazy('task_create')  # Redirect to task list after creating

# List Views
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'  # Context variable in the template

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/tasks.html'
    context_object_name = 'tasks'

    def get(self, request, *args, **kwargs):
        if 'label' in self.kwargs:
            self.project = get_object_or_404(Project, code=self.kwargs['label'].upper())
            return super().get(request, *args, **kwargs)
        else:
            form = ProjectSelectForm()
            return render(request, 'tasks/project_select.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = ProjectSelectForm(request.POST)
        if form.is_valid():
            project = form.cleaned_data['project']
            return redirect('task_lists', label=project.code)
        return render(request, 'tasks/project_select.html', {'form': form})

    def get_queryset(self):
        return Task.objects.filter(project=self.project)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context


# Detail View
class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/summary.html'
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


class TaskDetailView(DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'tasks/task_detail.html'
    pk_url_kwarg = 'unique_id'

    def get_object(self, queryset=None):
        label = self.kwargs.get('label')  # Extract 'label' from the URL
        unique_id = self.kwargs.get('unique_id')  # Extract 'unique_id' from the URL
        project = get_object_or_404(Project, code=label)
        task = get_object_or_404(Task, project=project, project_task_number=unique_id.split('-')[-1])
        return task

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = context['task']
        comments = Comment.objects.filter(task=task)
        context['comments'] = comments
        context['project'] = task.project  # Pass the related project to the context
        context['comment_form'] = CommentForm()  # Add the comment form to the context
        context['edit_form'] = CommentForm()
        # If editing a comment, add the edit form for that specific comment
        editing_comment_id = self.request.GET.get('editing_comment_id', None)  # Get the ID of the comment to edit
        if editing_comment_id:
            comment_to_edit = get_object_or_404(Comment, id=editing_comment_id)
            context['edit_form'] = CommentForm(instance=comment_to_edit)
        return context

    def post(self, request, *args, **kwargs):
        task = self.get_object()  # Retrieve the task object

        # Handle task description update
        if 'description' in request.POST:
            task.description = request.POST['description']
            task.save()
            return redirect('task_detail', label=task.project.code, unique_id=task.unique_id())

        # Handle comment update or deletion
        if 'comment_id' in request.POST:
            comment_id = request.POST['comment_id']
            comment = get_object_or_404(Comment, id=comment_id)

            if 'delete_comment' in request.POST:  # Handle comment deletion
                comment.delete()
            elif 'edit_comment' in request.POST:  # Handle comment update
                form = CommentForm(request.POST, request.FILES, instance=comment)
                if form.is_valid():
                    form.save()

            return redirect('task_detail', label=task.project.code, unique_id=task.unique_id())

        # Handle new comment creation
        form = CommentForm(request.POST, request.FILES)  # Use request.FILES for attachments
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.task = task  # Associate comment with the task
            new_comment.user = request.user  # Associate comment with the logged-in user
            new_comment.save()  # Save the comment

        return redirect('task_detail', label=task.project.code, unique_id=task.unique_id())

