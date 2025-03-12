from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from django.utils import timezone as tz
from django.utils.translation import activate, get_language
from django.conf import settings
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from account.models import Profile, Role, Department, Team, PasswordResetOTP, Invitation, OrgType, Organization
from account.forms import InvitationForm, PasswordResetRequestForm, OTPVerificationForm, SignUpForm, ProfileForm
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import RedirectView, DetailView, UpdateView, CreateView, DeleteView
from django.db.models import Count
from ctspms.models import Project, Task, Timelog

# Create your views here.

class RegisterView(View):
    def get(self, request):
        user_form = SignUpForm()
        return render(request, 'users/register.html', {'user_form': user_form})

    def post(self, request):
        user_form = SignUpForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()  # Save the user
            username = user.username  # Get the username of the newly created user

            # Log the user in after successful registration
            login(request, user)

            # Redirect to the profile setup page with the username
            return redirect(reverse('profile_setup', kwargs={'username': username}))  # Ensure it matches the new URL pattern

        return render(request, 'users/register.html', {'user_form': user_form})@method_decorator(login_required, name='dispatch')


class ProfileSetupView(View):
    def get(self, request, username):
        # Get the user by username
        user = User.objects.get(username=username)

        # Get the profile for this user, or create one if it doesn't exist
        profile, created = Profile.objects.get_or_create(user=user)

        # Create a form for the Profile model
        profile_form = ProfileForm(instance=profile)
        return render(request, 'users/../templates/profile/profile_setup.html', {'profile_form': profile_form, 'user': user})

    def post(self, request, username):
        # Get the user by username
        user = User.objects.get(username=username)

        # Get the profile for this user, or create one if it doesn't exist
        profile, created = Profile.objects.get_or_create(user=user)

        # Handle the form submission
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if profile_form.is_valid():
            profile_form.save()
            return redirect('dashboard')

        return render(request, 'users/../templates/profile/profile_setup.html', {'profile_form': profile_form, 'user': user})

class CommonDashboardDataMixin:
    def get_common_dashboard_data(self):
        projects = Project.objects.order_by('-start_date')[:5]
        tasks = Task.objects.order_by('-start_date')[:5]
        peoples = Profile.objects.all()
        teams = Team.objects.all()
        timelog = Timelog.objects.all()

        ts_no = Task.objects.count()
        prj_no = Project.objects.count()
        tk_status_no = Task.objects.filter(status__isnull=True).count()
        project_labels = [project.label() for project in projects]
        project_task_counts = [Task.objects.filter(project=project).count() for project in projects]

        return {
            'tk_status_no': tk_status_no,
            'prj_no': prj_no,
            'ts_no': ts_no,
            'projects': projects,
            'tasks': tasks,
            'profile': peoples,
            'timelog': timelog,
            'team': teams,
            'project_labels': project_labels,
            'project_task_counts': project_task_counts,
        }

@login_required
def dashboard_view(request):
    mixin = CommonDashboardDataMixin()
    context = mixin.get_common_dashboard_data()
    return render(request, 'dashboard.html', context)


def request_password_reset(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()

            if user:
                # Generate and save OTP for the user
                otp_entry = PasswordResetOTP.objects.create(user=user)
                otp = otp_entry.otp

                # Send OTP to the user's email
                send_mail(
                    'Password Reset OTP',
                    f'Your OTP for password reset is {otp}. It will expire in 10 minutes.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, 'OTP has been sent to your email.')
                return redirect('verify_otp', user_id=user.id)
            else:
                messages.error(request, 'No user found with that email address.')

    else:
        form = PasswordResetRequestForm()

    return render(request, 'users/request_password_reset.html', {'form': form})


# 2. Verify OTP and Reset Password
def verify_otp(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            new_password = form.cleaned_data['new_password']

            otp_entry = PasswordResetOTP.objects.filter(user=user, otp=otp).first()

            if otp_entry and otp_entry.is_valid():
                # Reset password
                user.set_password(new_password)
                user.save()

                # Mark OTP as used by deleting it
                otp_entry.delete()

                # Log the user in after password reset
                login(request, user)
                messages.success(request, 'Password reset successful. You are now logged in.')
                return redirect('dashboard')
            else:
                form.add_error('otp', 'Invalid or expired OTP.')

    else:
        form = OTPVerificationForm()

    return render(request, 'users/verify_otp.html', {'form': form, 'user': user})

# 3. Custom login view
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('dashboard')

    def get_success_url(self):
        # Clear old messages (if any) before setting the new one
        return self.success_url

    def form_invalid(self, form):
        """Handles invalid login attempts (e.g., wrong credentials)."""
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)


# 4. Logout view
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')  # Redirect to login page after logout

    def dispatch(self, request, *args, **kwargs):
        # Display a logout success message
        messages.success(request, "You have successfully logged out.")
        return super().dispatch(request, *args, **kwargs)


# 5. Dashboard view
@login_required  # Ensure that only logged-in users can access the dashboard
def dashboard_view(request):
    # Fetching data for the dashboard
    projects = Project.objects.order_by('-start_date')[:5]  # Limiting to 4 recent projects
    tasks = Task.objects.order_by('-start_date')[:5]
    peoples = Profile.objects.all()
    teams = Team.objects.all()
    timelog = Timelog.objects.all()

    # Get counts for projects and tasks
    ts_no = Task.objects.count()
    prj_no = Project.objects.count()

    # Status counts (example: count tasks with no status)
    tk_status_no = Task.objects.filter(status__isnull=True).count()

    # Get project labels and task counts for each project
    project_labels = [project.label() for project in projects]  # Project labels (e.g., 'HMS', 'PMS')

    # Aggregating task counts per project
    project_task_counts = [Task.objects.filter(project=project).count() for project in projects]

    return render(request, 'dashboard.html', {
        'tk_status_no': tk_status_no,
        'prj_no': prj_no,
        'ts_no': ts_no,
        'projects': projects,
        'tasks': tasks,
        'profile': peoples,
        'timelog': timelog,
        'team': teams,
        'project_labels': project_labels,  # Pass project labels
        'project_task_counts': project_task_counts,  # Pass project task counts
    })

@login_required
def settings_view(request):
    organizations = OrgType.objects.all()

    # if request.method == 'POST':
    #     # Get the selected timezone and language from the form
    #     selected_timezone = request.POST.get('timezone')
    #     selected_language = request.POST.get('language')
    #
    #     # Set the timezone in the user's session
    #     request.session['django_timezone'] = selected_timezone
    #     tz.activate(selected_timezone)  # Apply the timezone for this request
    #
    #     # Set the language in the user's session
    #     request.session[settings.LANGUAGE_COOKIE_NAME] = selected_language
    #     activate(selected_language)  # Apply the language for this request
    #
    #     # Redirect to the same page or any other page
    #     return redirect('your_page')
    #
    # # For GET requests, display the form
    # timezones = tz.common_timezones
    # languages = settings.LANGUAGES
    # current_timezone = tz.get_current_timezone_name()
    # current_language = get_language()

    return render(request, 'setting.html', {
        'organizations': organizations,
        # 'timezones': timezones,
        # 'languages': languages,
        # 'current_timezone': current_timezone,
        # 'current_language': current_language
    })

# 6. Invite user view
@login_required
def invite_user(request):
    if request.method == 'POST':
        form = InvitationForm(request.POST)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.invited_by = request.user  # Set the inviter to the current user
            invitation.save()

            # Send the user's email with a link
            invitation_link = request.build_absolute_uri(f"/accept-users/{invitation.code}/")
            send_mail(
                'You are invited to join!',
                f'Click here to accept the invitation: {invitation_link}',
                settings.DEFAULT_FROM_EMAIL,
                [invitation.email],
                fail_silently=False,
            )
            messages.success(request, 'Invitation sent successfully!')
            return redirect('invitation_success')
    else:
        form = InvitationForm()

    return render(request, 'users/invite_user.html', {'form': form})


# 7. Accept invitation and create user view
def accept_invitation(request, code):
    invitation = get_object_or_404(Invitation, code=code, accepted=False)  # Ensure the invite exists and hasn't been used

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            invitation.accepted = True  # Mark the invitation as accepted
            invitation.save()
            messages.success(request, 'Your account has been created successfully.')
            return redirect('login')  # Redirect to the login page after account creation
    else:
        form = UserCreationForm()

    return render(request, 'users/accept_invitation.html', {'form': form, 'invitation': invitation})


# 8. Invitation success view
def invitation_success(request):
    return render(request, 'users/invitation_success.html')


# 9. Password reset success view
def password_reset_success(request):
    return render(request, 'users/password_reset_success.html')


class ProfileDetailView(DetailView):
    model = Profile
    context_object_name = 'profile'
    template_name = 'profile/profile.html'

    def get_object(self):
        # Fetch profile by user UUID (assuming you're passing user_id in the URL)
        profile = Profile.objects.get(pk=self.kwargs['id'])
        team = Team.objects.all()
        return {'profile': profile, 'team': team}

class PeopleModify(UpdateView):
    model = Profile
