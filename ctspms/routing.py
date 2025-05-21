from django.urls import path
from ctspms import consumers

websocket_urlpatterns = [
    path("ws/notifation", consumers.NotificationConsumer.as_asgi()),
]
