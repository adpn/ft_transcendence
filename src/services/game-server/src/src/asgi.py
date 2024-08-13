"""
ASGI config for src project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django import setup
from django.core.asgi import get_asgi_application
from django.urls import re_path

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from common.game import GameServer
from pong.consumers import PongLogic

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
setup()
application = get_asgi_application()

URL_PATTERNS = [
	re_path(r'ws/game/pong/(?P<room_name>\w+)/$', GameServer.as_asgi(game_logic=PongLogic())),
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            URL_PATTERNS
        )
    ),
})
