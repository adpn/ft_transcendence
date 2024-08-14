import json
import abc
import asyncio
import queue

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.sessions.middleware import SessionMiddleware

from django.http import JsonResponse

import uuid

class Player:
	def __init__(self, player_id) -> None:
		self.player_id = player_id
	
class GameRoom:
	def __init__(self, room_name) -> None:
		self._num_players = 0
		self._room_name = room_name
		self._players = {}

	def num_players(self):
		return self._num_players
	
	@property
	def room_id(self):
		return self._room_name
	
	def add_player(self, player_id):
		self._num_players += 1
		self._players[player_id] = Player(player_id)
		return self._room_name
	
	def __contains__(self, value):
		return value in self._players

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

	def create_game_room(request):
		pass

	def get_game_session(self, room):
		if room not in self._self._game_sessions:
			self._game_sessions[room] = GameSession(self._game_factory.create_game()) # create new game logic for the game room.
		session = self._game_sessions[room]
		return session

	async def __aenter__(self):
		await self._lock.acquire()
		return self

	async def __aexit__(self):
		self._lock.release()


def create_game(request):
	player_id = request.session.get('player_id')
	
	# create new player
	if not player_id:
		player_id = str(uuid.uuid4())
		request.session['player_id'] = player_id

	# find a game room
	for game_room in games_rooms:
		player_id = request.session['player_id']
		if game_room.num_players == 1 and player_id not in game_room:
			# remove the game room
			games_rooms.remove(game_room)
			return JsonResponse({'game-room-id': game_room.add_player(player_id), 'status': 'ready'}, status=200)
	
	# create new game room if no game room was found.
	room = GameRoom(str(uuid.uuid4()))
	room.add_player(player_id)
	games_rooms.append(room)
	return JsonResponse({
		'game-room-id': room.add_player(player_id), 
		'player-id': player_id, 
		'status': 'waiting'}, status=200)

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
	
	async def get_session_key(self):
		return self.scope['session'].session_key

	async def connect(self):
		self.game_room = self.scope['url_route']['kwargs']['room_name']
		# hope this works
		session_key = await self.get_session_key()
		#reject any connection request that was not authenticated.
		if not session_key:
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
