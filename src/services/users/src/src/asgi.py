"""
ASGI config for src project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from django.urls import path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from user_data.online import OnlineStatusConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')

# Initialize Django ASGI application early to ensure the app registry is ready
django_asgi_app = get_asgi_application()

# URL Patterns for WebSocket connections
URL_PATTERNS = [
    path("status/", OnlineStatusConsumer.as_asgi()),  # WebSocket URL
]

# Define application protocol routing
application = ProtocolTypeRouter({
    'http': django_asgi_app,  # Handles HTTP requests
    'websocket': AuthMiddlewareStack(  # Ensure authentication in WebSocket connections
        URLRouter(URL_PATTERNS)
    ),
})
