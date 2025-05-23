# notifications.py
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def notify_user(notification):
    if not hasattr(notification.people, 'user'):
        return

    channel_layer = get_channel_layer()
    content = {
        "type": "send_notification",
        "content": {
            "id": str(notification.id),
            "title": "New Notification",
            "message": str(notification),
            "created_at": notification.created_at.isoformat(),
            "notification_type": notification.notification_type,
            "read": notification.read,
            "project_id": str(notification.project.id),
            "task_id": str(notification.task.id),
        }
    }

    async_to_sync(channel_layer.group_send)(
        f"user_{notification.people.user.id}",
        content
    )
