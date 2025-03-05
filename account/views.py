from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib import messages
from account.models import Profile, Role, Department, Member, PasswordResetOTP, Invitation
from account.forms import InvitationForm, PasswordResetRequestForm, OTPVerificationForm, SignUpForm
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import RedirectView, DetailView, UpdateView, CreateView, DeleteView
from django.db.models import Count
from ctspms.models import Project, Task, Timelog

# Create your views here.
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
    members = Member.objects.all()
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
        'peoples': peoples,
        'timelog': timelog,
        'members': members,
        'project_labels': project_labels,  # Pass project labels
        'project_task_counts': project_task_counts,  # Pass project task counts
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


class PeopleView(DetailView):
    model = Profile
    context_object_name = 'peoples'
    template_name = 'peoples/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

class PeopleModify(UpdateView):
    model = Profile
