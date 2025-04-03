from django.urls import path
from account.views import RegisterView, ProfileSetupView, CustomLoginView, two_factor_auth_view, CustomLogoutView, ProfileDetailView, UserProfileDetailView, TeamView, TeamCreateView, TeamDetailView, dashboard_view, settings_view, invite_user, accept_invitation, invitation_success, request_password_reset, verify_otp, password_reset_success, user_search

# Create your tests here.

urlpatterns = [
    # Authentication
    path('', CustomLoginView.as_view(), name='login'),
    path('verify/2fa/', two_factor_auth_view, name='two_factor_auth'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/setup/<str:username>', ProfileSetupView.as_view(), name='profile_setup'),
    # Dashboard
    path('dashboard/', dashboard_view, name='dashboard'),
    path('settings/', settings_view, name='settings'),

    path('invite/', invite_user, name='invite_user'),
    path('accept-users/<str:code>/', accept_invitation, name='accept_invitation'),
    path('users-success/', invitation_success, name='invitation_success'),

    path('reset-password/', request_password_reset, name='password_reset'),
    path('verify-otp/<int:user_id>/', verify_otp, name='verify_otp'),
    path('password-reset-success/', password_reset_success, name='password_reset_success'),
    path('profile/<str:id>', ProfileDetailView.as_view(), name='profile'),
    path('user/<str:user_id>/', UserProfileDetailView.as_view(), name='user_profile'),
    path('teams/<uuid:id>/', TeamDetailView.as_view(), name='team_detail'),
    path('user-search/', user_search, name='user_search'),
    # path('profile/edit/', PeopleModify.as_view(), name='profile-edit')
    path('teams/', TeamView.as_view(), name='teams'),
    path('teams/create/', TeamCreateView.as_view(), name='team_create'),
]