import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path, re_path
from administrators.consumers import DashboardConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path(r"ws/dashboard/(?P<department>[^/]+)/$", DashboardConsumer.as_asgi()),
            re_path(r"ws/dashboard/$", DashboardConsumer.as_asgi()),
        ])
    ),
})
