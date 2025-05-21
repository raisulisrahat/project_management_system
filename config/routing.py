from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import ctspms.routing  # app level

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(
            ctspms.routing.websocket_urlpatterns
        )
    ),
})
