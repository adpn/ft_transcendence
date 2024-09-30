from channels.middleware import BaseMiddleware
from django.db import close_old_connections
from games.models import GameRoom
from channels.exceptions import DenyConnection

from common import auth_client as auth

class GameRoomAuthMiddleware(BaseMiddleware):
	async def __call__(self, scope, receive, send):
		close_old_connections()

		game_room = self.scope['url_route']['kwargs']['room_name']

		query_string = scope.get('query_string').decode('utf-8')
		params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
		token = params.get('token')
		csrf = params.get('csrf')
		if not token and not csrf:
			# If the room does not exist, close the connection
			await send({
				"type": "websocket.close",
				"code": 4000,  # Custom close code
				"reason": "Tokens is missing."
			})
			raise DenyConnection("Tokens is missing.")

		user = auth.get_user_with_token(token, csrf)

		if not user:
			# If the room does not exist, close the connection
			await send({
				"type": "websocket.close",
				"code": 4000,  # Custom close code
				"reason": "Invalid token."
			})
			raise DenyConnection("Invalid token.")

		room = GameRoom.objects.filter(room_name=game_room).first()
		if not room:
            # If the room does not exist, close the connection
			await send({
				"type": "websocket.close",
				"code": 4000,  # Custom close code
				"reason": "Invalid game room."
			})
			raise DenyConnection("Invalid game room.")

		# Call the next middleware or the consumer
		return await super().__call__(scope, receive, send)
