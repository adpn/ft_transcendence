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
def get_player_room(user_id, game_room):
    return PlayerRoom.objects.filter(
        player__player_id=user_id, 
        game_room__room_name=game_room
    ).first()

@database_sync_to_async
def get_expected_players(player_room):
    # Access the player_count in a synchronous context
    return player_room.game_room.expected_players

@database_sync_to_async
def get_player_id(player_room):
    # Access the player_count in a synchronous context
    return player_room.player.player_id

@database_sync_to_async
def set_player_position(player_room, position):
	player_room.player_position = position
	player_room.save()

@database_sync_to_async
def get_player_position(player_room):
	return player_room.player_position

@database_sync_to_async
def set_in_session(player_room):
	player_room.game_room.in_session = True
	player_room.game_room.save()



@database_sync_to_async
def in_session(player_room):
	return player_room.game_room.in_session

class GameConsumer(AsyncWebsocketConsumer):
	def __init__(self, game_server, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._game_server = game_server
		self._game_session = None
		self.disconnected = False

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

		# todo: send error messages to user.
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
		self.player_room = player_room = await get_player_room(user['user_id'], game_room)

		# todo: send error messages to user.
		if not player_room:
			await self.accept()
			# await self.send({
			# 	"type": "websocket.close",
			# 	"code": 4000,  # Custom close code
			# 	"reason": "Player has no game room."
			# })
			self.close()
			return

		expected_players = await get_expected_players(player_room)
		# create new game session if none exists.
		async with self._game_server as server:
			session = server.get_game_session(self.game_room)
			await self.channel_layer.group_add(self.game_room, self.channel_name)
			# if the amount of players is met, notify all clients.
			self.player = await get_player_position(player_room)
			#await set_player_position(player_room, session.current_players)
			session.current_players += 1
			if session.current_players == expected_players:
				# keep a reference to the game session.
				self._game_session = session
				await self.accept()
				# send ready notification.
				await self.channel_layer.group_send(
				self.game_room,
				{
					'type': 'game_status',
					'message': {'status': 'ready'}
				})
				self._game_session.on_session_end(self.flush_game_session)
				# only start new game loop if no game is in session.
				if not await in_session(player_room):
					asyncio.create_task(self._game_session.start(self.state_callback))
				await set_in_session(player_room)
			elif session.current_players < expected_players:
				session.on_session_end(self.flush_game_session)
				await self.accept()
				self._game_session = session
				await self.channel_layer.group_send(
				self.game_room,
				{
					'type': 'game_status',
					'message': {'status': 'waiting'}
				})
			# todo: we do not need this because we never get to this point
			# refuse connection if the game is full
			elif session.current_players > expected_players:
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
		session = self._game_server.get_game_session(self.game_room)
		session.current_players -= 1
		# todo: don't remove if already removed
		try:
			session._end_callbacks.remove(self.flush_game_session)
		except ValueError:
			pass
		# todo: if a player disconnects should pause the game...
		# if not self._game_session:
		await self.channel_layer.group_discard(self.game_room, self.channel_name)
		self.disconnected = True
		# room = self._game_session
		# room.current_players -= 1
		# if room.current_players <= 0:
		# 	await self.channel_layer.group_discard(self.game_room, self.channel_name)

	# receives data from websocket.
	# todo: if there are no player a
	async def receive(self, bytes_data):
		if self.disconnected:
			return 
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
