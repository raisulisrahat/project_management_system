from django.db import models
from django.utils.crypto import get_random_string
from django.utils import timezone
import uuid, pyotp
from django.contrib.auth.models import User, Group
import datetime
from django.core.exceptions import ValidationError


# Create your models here.
class OrgType(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Organization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.OneToOneField(OrgType, on_delete=models.CASCADE, max_length=100)

    def __str__(self):
        return self.name


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role_name = models.CharField(max_length=100)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return self.role_name

class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department_name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='departments')
    def __str__(self):
        return self.department_name

class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    user_id = models.ManyToManyField(User, related_name='teams')

    def __str__(self):
        return self.name

class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.ImageField(upload_to='upload/images/', null=True, blank=True, default='/images/user.png')
    country = models.ForeignKey('cities_light.Country', on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    teams = models.ManyToManyField(Team, blank=True)
    timezone = models.CharField(max_length=100, default='UTC')
    language = models.CharField(max_length=10, default='en')
    two_factor_enabled = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=32, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Generate a new TOTP secret if enabling 2FA and no secret exists
        if self.two_factor_enabled and not self.totp_secret:
            self.totp_secret = pyotp.random_base32()
        super().save(*args, **kwargs)

    def validate_image(self):
        if not self.profile_image.name.endswith(('.png', '.jpg', '.jpeg')):
            raise ValidationError('Invalid file format. Only PNG and JPG allowed.')

    def full_name(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def __str__(self):
        return self.full_name()

class Invitation(models.Model):
    email = models.EmailField(unique=True)  # Email of the invited person
    code = models.CharField(max_length=64, unique=True)  # Unique users code
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE)  # User who invited
    created_at = models.DateTimeField(default=timezone.now)
    accepted = models.BooleanField(default=False)  # Track if the invite was accepted

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = get_random_string(64)  # Generate a random 64-character users code
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)  # 6-digit OTP code
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.otp:
            self.otp = get_random_string(6, allowed_chars='0123456789')  # Generate a 6-digit numeric OTP
        if not self.expires_at:
            self.expires_at = timezone.now() + datetime.timedelta(minutes=10)  # OTP expires in 10 minutes
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() < self.expires_at

    def __str__(self):
        return f'OTP for {self.user.email}'