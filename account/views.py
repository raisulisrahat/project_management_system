from datetime import timezone
from django.dispatch import receiver
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
import pytz, pyotp, io, qrcode, base64, logging
from django.conf import settings
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from account.models import Profile, Role, Department, Team, PasswordResetOTP, Invitation, OrgType, Organization
from account.forms import InvitationForm, PasswordResetRequestForm, OTPVerificationForm, SignUpForm, ProfileForm
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import RedirectView, DetailView, UpdateView, CreateView, DeleteView, ListView
from django.db.models import Count
from ctspms.models import Project, Task, Timelog

# Create your views here.
# logs
logger = logging.getLogger(__name__)
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

        return render(request, 'users/register.html', {'user_form': user_form})
    
    
    
@method_decorator(login_required, name='dispatch')
class ProfileSetupView(View):
    def get(self, request, username):
        # Get the user by username
        user = User.objects.get(username=username)

        # Get the profile for this user, or create one if it doesn't exist
        profile, created = Profile.objects.get_or_create(user=user)

        # Create a form for the Profile model
        profile_form = ProfileForm(instance=profile)
        return render(request, 'profile/profile_setup.html', {'profile_form': profile_form, 'user': user})

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

        return render(request, 'profile/profile_setup.html', {'profile_form': profile_form, 'user': user})

class CommonDashboardDataMixin:
    def get_common_dashboard_data(self):
        projects = Project.objects.order_by('-start_date')[:5]
        tasks = Task.objects.order_by('-start_date')[:5]
        peoples = Profile.objects.all()
        team = Team.objects.all()
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
            'team': team,
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

    def form_valid(self, form):
        """Override this method to handle 2FA after valid credentials are entered."""
        user = form.get_user()

        # Apply timezone and language settings from the user's profile
        self.request.session['django_timezone'] = user.profile.timezone
        self.request.session['django_language'] = user.profile.language

        # Check if the user has 2FA enabled
        if user.profile.two_factor_enabled:
            self.request.session['2fa_user_id'] = user.id
            return redirect('two_factor_auth')
        else:
            login(self.request, user)
            return redirect(self.get_success_url())

    def form_invalid(self, form):
        """Handles invalid login attempts (e.g., wrong credentials)."""
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)

    def get_success_url(self):
        """Redirect to the dashboard on successful login."""
        return self.success_url


@login_required
def two_factor_auth_view(request):
    """View to handle 2FA code input and validation."""
    if request.method == 'POST':
        token = request.POST.get('token')
        user_id = request.session.get('2fa_user_id')

        if user_id:
            user = User.objects.get(id=user_id)
            totp = pyotp.TOTP(user.profile.totp_secret)

            # Verify the 2FA token
            if totp.verify(token):
                # Token is valid, log the user in and clear session data
                login(request, user)
                del request.session['2fa_user_id']  # Clear session data after successful login
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid 2FA code. Please try again.")
        else:
            messages.error(request, "An error occurred. Please try again.")

    return render(request, 'users/2fa.html')
# 4. Logout view
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')  # Redirect to login page after logout

    def dispatch(self, request, *args, **kwargs):
        # Display a logout success message
        messages.success(request, "You have successfully logged out.")
        return super().dispatch(request, *args, **kwargs)


@login_required
def settings_view(request):
    timezones = pytz.all_timezones  # List of all timezones
    languages = settings.LANGUAGES  # List of available languages
    profile = request.user.profile  # Get the user's profile

    # Generate or retrieve TOTP secret from the user's profile (instead of session)
    if not profile.totp_secret:
        profile.totp_secret = pyotp.random_base32()  # Generate a random secret for TOTP

    # Generate the TOTP object and provisioning URL
    totp = pyotp.TOTP(profile.totp_secret)
    totp_url = totp.provisioning_uri(name=request.user.email, issuer_name="Flowtrex")

    # Generate a QR code for the TOTP URL
    qr_img = qrcode.make(totp_url)
    buf = io.BytesIO()
    qr_img.save(buf, format='PNG')
    qr_code_data = base64.b64encode(buf.getvalue()).decode()  # Encode as base64 for rendering

    # Track whether 2FA is enabled or disabled
    two_factor_state = profile.two_factor_enabled
    show_modal = False  # Track if modal should be shown

    if request.method == 'POST':
        # Get the submitted form values (timezone, language, 2FA state, and 2FA token)
        selected_timezone = request.POST.get('timezone')
        selected_language = request.POST.get('language')
        selected_2fa_state = request.POST.get('2fa_state')
        submitted_token = request.POST.get('token')

        # Update profile timezone and language
        profile.timezone = selected_timezone
        profile.language = selected_language

        # Enable or disable 2FA based on selection
        if selected_2fa_state == 'enable':
            show_modal = True
            if submitted_token:
                # Verify the TOTP token
                if totp.verify(submitted_token):
                    profile.two_factor_enabled = True  # Mark 2FA as enabled
                    profile.save()  # Save changes to profile
                    show_modal = False  # Close modal after successful token submission
                else:
                    request.session['2fa_error'] = "Invalid token"  # Token is invalid
                    show_modal = True  # Keep modal open if token is invalid
        elif selected_2fa_state == 'disable':
            profile.two_factor_enabled = False  # Disable 2FA
            profile.save()

        return redirect('settings')

    # Add current settings to context
    context = {
        'timezones': timezones,
        'languages': languages,
        'current_timezone': profile.timezone,
        'current_language': profile.language,
        'qr_code_data': qr_code_data,  # QR code data as base64 for 2FA
        '2fa_enabled': profile.two_factor_enabled,
        '2fa_error': request.session.get('2fa_error', ''),
        'show_modal': show_modal,  # Pass modal visibility status
    }

    return render(request, 'setting.html', context)


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

class TeamView(ListView):
    model = Team
    context_object_name = 'team'
    template_name = "teams/teams.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_list'] = User.objects.filter(profile__isnull=False)  # Users with profiles
        context['team_list'] = Team.objects.all()  # All teams
        return context

