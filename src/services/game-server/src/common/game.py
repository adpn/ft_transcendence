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
	def __init__(self, game_logic):
		self._game_logic = game_logic
		# self._queue = asyncio.Queue(5)
		self.current_players = 0
		self.min_players = 2

	async def update(self, data, player):
		# await self._queue.put(data)
		await self._game_logic.updateInput(data[0], data[1], player)

	async def start(self, callback):
		while True:					# concatanate maybe when it works
			# data = await self._queue.get()
			# data = await self._game_logic.update(data)
			data = await self._game_logic.gameTick()
			await callback(data)
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
		if room not in self._game_sessions:
			self._game_sessions[room] = GameSession(self._game_factory()) # create new game logic for the game room.
		session = self._game_sessions[room]
		return session

	async def check_room(self, room_id):
		return self.SessionStore(room_id).exists(room_id)

	async def __aenter__(self):
		await self._lock.acquire()
		return self

	async def __aexit__(self, exc_type, exc_value, exc_tb):
		self._lock.release()

class GameLogic(abc.ABC):
	@abc.abstractmethod
	async def updateInput(data):
		pass
	async def gameTick():
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
				# todo: set _game_session of all players to room
				await self.accept()
				# send ready notification.
				await self.channel_layer.group_send(
				self.game_room,
				{
					'type': 'game_status',
					'message': {'status': 'ready'}
				})
				# start game loop for the session.
				asyncio.create_task(self._game_session.start(self.state_callback))
			elif room.current_players < room.min_players:
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

	async def disconnect(self, close_code):
		# todo: remove game room from session store.
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
