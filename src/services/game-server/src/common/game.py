import json
import abc
import asyncio
import queue

from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.http import JsonResponse

from importlib import import_module
import uuid

class Player:
	def __init__(self, player_id) -> None:
		self.player_id = player_id


class GameSession(object):
	def __init__(self, players, game_logic):
		self._players = players
		self._game_logic = game_logic
		self._queue = queue.Queue(5)

	async def update(self, data):
		self._queue.put(data)

	async def start(self, callback):
		while True:
			await callback(self._game_logic.update(self._queue.get()))
			await asyncio.sleep(0.05)

class GameServer(object):
	def __init__(self, game_factory):
		self._game_sessions = {}
		self._rooms = []
		self._lock = asyncio.Lock()
		self._game_factory = game_factory
		engine = import_module(settings.SESSION_ENGINE)
		self.SessionStore = engine.SessionStore

	def get_game_session(self, room):
		if room not in self._self._game_sessions:
			self._game_sessions[room] = GameSession(self._game_factory.create_game()) # create new game logic for the game room.
		session = self._game_sessions[room]
		return session
	
	async def check_room(self, room_id):
		return self.SessionStore(room_id).exists(room_id)

	async def __aenter__(self):
		await self._lock.acquire()
		return self

	async def __aexit__(self):
		self._lock.release()

class GameLogic(abc.ABC):
	@abc.abstractmethod
	def update(data):
		pass

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
		self.game_room = self.scope['url_route']['kwargs']['room_name']

		#reject any invalid room_name.
		if not await self._game_server.check_room(self.game_room):
			await self.close()

		# todo: need a game logic factory
		# create new game session if none exists.
		async with self._game_server as server:
			room = server.get_game_session(self.game_room)
			await self.channel_layer.group_add(self.game_room, self.channel_name)
			# if the amount of players is met, notify all clients.
			room.current_players += 1
			if room.current_players == room.min_players:
				await self.channel_layer.group_send(
				self.game_room,
				{
					'type': 'game_status',
					'message': 'ready'
				})
				# keep a reference to the game session.
				self._game_session = room
				await self.accept()
				# start game loop for the session.
				asyncio.create_task(self._game_session.start(self.state_callback))
			elif room.num_players < self._game_settings.min_players:
				await self.channel_layer.group_send(
				self.game_room,
				{
					'type': 'game_status',
					'message': {'status' : 'waiting'}
				})
				await self.accept()
			# refuse connection if the game is full
			elif room.num_players > self._game_settings.min_players:
				await self.channel_layer.group_send(
				self.game_room,
				{
					'type': 'game_status',
					'message': {'status' : 'full'}
				})
				# close connection
				await self.accept()
				await self.close()

	async def disconnect(self, close_code):
		# todo: remove game room from session store.
		self.game_room = self.scope['url_route']['kwargs']['room_name']
		if not self._game_session:
			await self.channel_layer.group_discard(self.game_room, self.channel_name)
		room = self._game_session
		room.num_players -= 1
		if room.num_players <= 0:
			await self.channel_layer.group_discard(self.game_room, self.channel_name)

	# receives data from websocket.
	# todo: if there are no player a
	async def receive(self, text_data):
		if self._game_session:
			data = json.loads(text_data)
			# Broadcast to group
			# todo: if game is not ready update all
			await self._game_session.update(data)
		else:
			await self.channel_layer.group_send(
				self.game_room,
				{
					'type': 'game_state',
					'message': {},
				}
			)

	async def game_state(self, event):
		await self.send(text_data=json.dumps(event['message']))
	
	async def game_status(self, event):
		await self.send(text_data=json.dumps(event['message']))
