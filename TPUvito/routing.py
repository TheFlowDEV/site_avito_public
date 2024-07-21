from .chat.consumer import ChatConsumer
from .notifications.notification import NotificationConsumer
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

websocket_urlpatterns=[
                    path(
                        "ws/chat",ChatConsumer.as_asgi()
                    ),
                    path('ws/notify',NotificationConsumer.as_asgi())
                ]

application = ProtocolTypeRouter( 
    {
        "websocket": AuthMiddlewareStack(
            URLRouter(
               websocket_urlpatterns
            )
        ),
    }
)