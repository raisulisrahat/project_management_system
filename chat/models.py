from django.db import models
from account.models import User, Profile

# Create your models here.
class Meeting(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    participants = models.ManyToManyField(Profile, blank=True)
