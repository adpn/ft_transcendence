import json
import abc
import asyncio
import os
import django

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from common import auth_client as auth
from games.models import PlayerRoom

class GameSession(object):
	def __init__(self, game_logic, game_server, session_id):
		self._game_logic = game_logic
		self.current_players = 0
		self.min_players = 2
		self._game_server = game_server
		self._session_id = session_id
		self._end_callbacks = []

	async def update(self, data, player):
		await self._game_logic.update(data, player)

	async def start(self, callback):
		await callback(await self._game_logic.startEvent())
		while True:					# concatanate maybe when it works
			data = await self._game_logic.sendEvent()
			while data:
				if data["type"] == "win":
					del self._game_server._game_sessions[self._session_id]
					for end in self._end_callbacks:
						await end(data["player"])
					return
				await callback(data)
				data = await self._game_logic.sendEvent()
			data = await self._game_logic.gameTick()
			await callback(data)
			await asyncio.sleep(0.03)

	def on_session_end(self, callback):
		self._end_callbacks.append(callback)

class GameServer(object):
	def __init__(self, game_factory):
		self._game_sessions = {}
		self._rooms = []
		self._lock = asyncio.Lock()
		self._game_factory = game_factory

	def get_game_session(self, room):
		if room not in self._game_sessions:
			self._game_sessions[room] = GameSession(self._game_factory(), self, room) # create new game logic for the game room.
		session = self._game_sessions[room]
		return session

	async def __aenter__(self):
		await self._lock.acquire()
		return self

	async def __aexit__(self, exc_type, exc_value, exc_tb):
		self._lock.release()

class GameLogic(abc.ABC):
	@abc.abstractmethod
	async def startEvent():
		pass
	async def gameTick():
		pass
	async def update(data, player):
		pass
	async def sendEvent():
		pass

@database_sync_to_async
def get_room_player(user_id, game_room):
    return PlayerRoom.objects.filter(
        player__player_id=user_id, 
        game_room__room_name=game_room
    ).first()

class GameConsumer(AsyncWebsocketConsumer):
	def __init__(self, game_server, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._game_server = game_server
		self._game_session = None

	async def state_callback(self, data):
		await self.channel_layer.group_send(
				self.game_room,
				{
					'type': 'game_state',
					'message': data
				}
			)

	async def connect(self):
		self.game_room = game_room = self.scope['url_route']['kwargs']['room_name']

		game_room = self.scope['url_route']['kwargs']['room_name']
		
		query_string = self.scope.get('query_string').decode('utf-8')
		params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
		token = params.get('token')
		csrf = params.get('csrf_token')
		if not token and not csrf:
			# If the room does not exist, close the connection
			await self.accept()
			# await self.send({
			# 	"type": "websocket.close",
			# 	"code": 4000,  # Custom close code
			# 	"reason": "Tokens are missing."
			# })
			await self.close()
			return

		# todo: might need to specify csrf ?
		user = auth.get_user_with_token(token, csrf)

		if not user:
			# If the room does not exist, close the connection
			await self.accept()
			# await self.send({
			# 	"type": "websocket.close",
			# 	"code": 4000,  # Custom close code
			# 	"reason": "Invalid tokens."
			# })
			self.close()
			return 

		# room_player = RoomPlayer.objects.filter(game_room=game_room, 
		# player=user['user-id']).first()
		room_player = await get_room_player(user['user_id'], game_room)

		if not room_player:
			await self.accept()
			# await self.send({
			# 	"type": "websocket.close",
			# 	"code": 4000,  # Custom close code
			# 	"reason": "Player has no game room."
			# })
			self.close()
			return

		#reject any invalid room_name.
		# if not await self._game_server.check_room(self.game_room):
		# 	await self.close()

		# todo: need a game logic factory
		# create new game session if none exists.
		async with self._game_server as server:
			room = server.get_game_session(self.game_room)
			await self.channel_layer.group_add(self.game_room, self.channel_name)
			# if the amount of players is met, notify all clients.
			self.player = room.current_players
			room.current_players += 1
			if room.current_players == room.min_players:
				# keep a reference to the game session.
				self._game_session = room
				await self.accept()
				# send ready notification.
				await self.channel_layer.group_send(
				self.game_room,
				{
					'type': 'game_status',
					'message': {'status': 'ready'}
				})
				self._game_session.on_session_end(self.flush_game_session)
				# start game loop for the session.
				asyncio.create_task(self._game_session.start(self.state_callback))
			elif room.current_players < room.min_players:
				room.on_session_end(self.flush_game_session)
				await self.accept()
				self._game_session = room
				await self.channel_layer.group_send(
				self.game_room,
				{
					'type': 'game_status',
					'message': {'status': 'waiting'}
				})
			# refuse connection if the game is full
			elif room.current_players > room.min_players:
				# close connection
				await self.accept()
				await self.channel_layer.group_send(
				self.game_room,
				{
					'type': 'game_status',
					'message': {'status': 'full'}
				})
				await self.close()

	async def flush_game_session(self, player):
		if self.player == player:
			data = { "type": "win", "player": 1 }
		else:
			data = { "type": "win", "player": 0 }
		await self.send(text_data=json.dumps(data))
		await self.channel_layer.group_discard(self.game_room, self.channel_name)
		# await self.close()	# no rematching

# is this ft in use ? (also add a del room.on_session_end(self.flush_game_session) type deal)
	async def disconnect(self, close_code):
		self.game_room = self.scope['url_route']['kwargs']['room_name']
		if not self._game_session:
			await self.channel_layer.group_discard(self.game_room, self.channel_name)
		room = self._game_session
		room.current_players -= 1
		if room.current_players <= 0:
			await self.channel_layer.group_discard(self.game_room, self.channel_name)

	# receives data from websocket.
	# todo: if there are no player a
	async def receive(self, bytes_data):
		if self._game_session:
			# Broadcast to group
			# todo: if game is not ready update all
			await self._game_session.update(bytes_data, self.player)
		else:
			await self.channel_layer.group_send(
				self.game_room,
				{
					'type': 'game_state',
					'message': {'status': 'no session'}
				}
			)

	async def game_state(self, event):
		await self.send(text_data=json.dumps(event['message']))

	async def game_status(self, event):
		await self.send(text_data=json.dumps(event['message']))
