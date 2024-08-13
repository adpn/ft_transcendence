import json
import abc
import asyncio
import queue

from channels.generic.websocket import AsyncWebsocketConsumer

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

games_rooms = []

def create_game(request):
    # ws_address = f'{str(uuid.uuid4())}'
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
	return JsonResponse({'game-room-id': room.add_player(player_id), 'status': 'waiting'}, status=200)

class GameLogic(abc.ABC):
	@abc.abstractclassmethod
	def update(data):
		pass

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
			

GAME_SESSIONS = {}
LOCK = asyncio.Lock()

class GameServer(AsyncWebsocketConsumer):
	def __init__(self, game_logic, game_settings, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._game_logic = game_logic
		self._game_settings = game_settings
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
		# todo: need a game logic factory
		# create new game session if none exists.
		async with LOCK:
			if self.game_room not in GAME_SESSIONS:
				GAME_SESSIONS[self.game_room] = GameSession(self._game_logic()) # create new game logic for the game room.
			room = GAME_SESSIONS[self.game_room]
			await self.channel_layer.group_add(self.game_room, self.channel_name)
			# if the amount of players is met, notify all clients.
			room.num_players += 1
			if room.num_players == self._game_settings.min_players:
				await self.channel_layer.group_send(
				self.game_room,
				{
					'type': 'game_status',
					'message': 'ready'
				})
				# reserve the game session.
				self._game_session = GAME_SESSIONS[self.game_room]
				# todo: 
				await self.accept()
				# start game loop
				asyncio.create_task(self._game_session.start(self.state_callback))
			elif room.num_players < self._game_settings.min_players:
				await self.channel_layer.group_send(
				self.game_room,
				{
					'type': 'game_status',
					'message': 'waiting'
				})
				await self.accept()
			# refuse connection if the fame is full
			elif room.num_players > self._game_settings.min_players:
				await self.channel_layer.group_send(
				self.game_room,
				{
					'type': 'game_status',
					'message': 'full'
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
