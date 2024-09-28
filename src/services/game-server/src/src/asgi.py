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

from channels.routing import ProtocolTypeRouter, URLRouter

from common.game_server import GameConsumer, GameServer
from pong.consumers import PongLogic
from snake.consumers import SnakeLogic

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
setup()

PONG_SERVER = GameServer(PongLogic)
SNAKE_SERVER = GameServer(SnakeLogic)

URL_PATTERNS = [
	path("game/pong/<str:room_name>/", GameConsumer.as_asgi(game_server=PONG_SERVER)),
	path("game/snake/<str:room_name>/", GameConsumer.as_asgi(game_server=SNAKE_SERVER))
]

#     'websocket': AuthMiddlewareStack(
#         URLRouter(
#             URL_PATTERNS
#         )
#     ),

application = ProtocolTypeRouter({
	'http': get_asgi_application(),
	'websocket': URLRouter(URL_PATTERNS)
})
