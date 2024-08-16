"""
ASGI config for src project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django import setup
from django.core.asgi import get_asgi_application
from django.urls import path

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from common.game import GameConsumer, GameServer
from pong.consumers import PongLogic

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
setup()
application = get_asgi_application()

PONG_SERVER = GameServer(PongLogic)

URL_PATTERNS = [
	path("ws/pong/<str:room_name>", GameConsumer.as_asgi(game_server=PONG_SERVER))
]

application = ProtocolTypeRouter({
    # 'websocket': AuthMiddlewareStack(
    #     URLRouter(
    #         URL_PATTERNS
    #     )
    # ),
	'websocket': URLRouter(URL_PATTERNS)
})
