from django.urls import re_path
from ctspms.consumers import NotificationConsumer

websocket_urlpatterns = [
    re_path("ws/notifation/$", NotificationConsumer.as_asgi()),
]
