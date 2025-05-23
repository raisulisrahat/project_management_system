# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task, Notification
from ctspms.notifications import notify_user  # <-- safe to import now

@receiver(post_save, sender=Task)
def send_task_assigned_notification(sender, instance, created, **kwargs):
    if instance.assigned_to:
        if not created:
            try:
                old = Task.objects.get(pk=instance.pk)
                if old.assigned_to != instance.assigned_to:
                    notification = Notification.objects.create(
                        notification_type='task_assigned',
                        people=instance.assigned_to,
                        project=instance.project,
                        task=instance,
                        comment=None,
                    )
                    notify_user(notification)
            except Task.DoesNotExist:
                pass
        else:
            notification = Notification.objects.create(
                notification_type='task_assigned',
                people=instance.assigned_to,
                project=instance.project,
                task=instance,
                comment=None,
            )
            notify_user(notification)


