import json
import abc
import asyncio
import os
import django
import time

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from common import auth_client as auth
from games.models import PlayerRoom, GameResult

@database_sync_to_async
def get_player_room(user_id, game_room):
    return PlayerRoom.objects.filter(
        player__player_id=user_id,
        game_room__room_name=game_room
    ).first()

@database_sync_to_async
def get_player_room_player(player_room):
    return player_room.player

@database_sync_to_async
def get_expected_players(player_room):
    return player_room.game_room.expected_players

@database_sync_to_async
def get_player_id(player_room):
    return player_room.player.player_id

@database_sync_to_async
def set_player_position(player_room, position):
	player_room.player_position = position
	player_room.save()

@database_sync_to_async
def get_player_position(player_room):
	return player_room.player_position

@database_sync_to_async
def get_game_room(player_room):
	return player_room.game_room

@database_sync_to_async
def get_game_room_game(game_room):
	return game_room.game

@database_sync_to_async
def set_in_session(game_room, value: bool):
	game_room.in_session = value
	# ! important ! it is important to spefify that this is the only field that needs to be updated
	# otherwise the game room data gets overwritten with old data
	game_room.save(update_fields=['in_session'])

@database_sync_to_async
def set_player_count(game_room, value: int):
	game_room.player_count = value
	game_room.save()

@database_sync_to_async
def in_session(game_room):
	return game_room.in_session

@database_sync_to_async
def get_min_players(game_room):
	return game_room.game.min_players

@database_sync_to_async
def delete_game_room(game_room):
	game_room.delete()

@database_sync_to_async
def store_game_result(game_result):
	game_result.save()

class GameSession(object):
	def __init__(self, game_logic, game_server, game_room, pause_timeout=30):
		self._game_logic = game_logic
		self.current_players = 0
		self._game_room = game_room
		self._game_server = game_server
		self._session_id = game_room.room_name
		self._end_callbacks = []
		self._connection_lost_callbacks = []
		self._pause_event = asyncio.Event()
		self._pause_event.set()
		self._timeout = pause_timeout
		self.is_running = True
		self._players = [None, None]
		self._game_result = GameResult()

	def set_player(self, position, player):
		self._players[position] = player

	async def update(self, data, player):
		await self._game_logic.update(data, player)

	async def start(self, callback):
		await callback(await self._game_logic.startEvent())
		t0 = time.time()
		while self.is_running:
			await asyncio.gather(
				self.game_loop(callback),
				asyncio.sleep(0.03)				# about 30 loops/second
			)
		self._game_result.game_duration = time.time() - t0
		await store_game_result(self._game_result)
		await delete_game_room(self._game_room)

	async def game_loop(self, callback):
		try:
			await asyncio.wait_for(self._pause_event.wait(), self._timeout)
		except asyncio.TimeoutError:
			for end in self._connection_lost_callbacks:
				await end()
			await set_in_session(self._game_room, False)
			# todo: on connection lost, game results should be stored
			# by the game consumers.
			#await store_game_result(game_result)
			return
		data = await self._game_logic.gameTick()
		await callback(data)
		async for data in self._game_logic.sendEvent():
			if data["type"] == "win":
				self._game_server.remove_session(self._session_id)
				for end in self._end_callbacks:
					await end(data)
				await set_in_session(self._game_room, False)
				# todo: store game results and delete the game room
				self._game_result = GameResult(
					winner=self._players[data["player"]],
					loser=self._players[data["loser"]],
					winner_score=data["score"][data["player"]],
					loser_score=data["score"][data["loser"]],
					game=await get_game_room_game(self._game_room))
				self.is_running = False
				return
			await callback(data)
			await asyncio.sleep(0.001)

	def on_session_end(self, callback):
		self._end_callbacks.append(callback)

	def remove_callback(self, event, callback):
		try:
			if event == 'session-end':
				self._end_callbacks.remove(callback)
			elif event == 'connection-lost':
				self._connection_lost_callbacks.remove(callback)
		except ValueError:
			pass

	def on_connection_lost(self, callback):
		self._connection_lost_callbacks.append(callback)

	def pause(self):
		self._pause_event.clear()

	def resume(self):
		self._pause_event.set()

class GameServer(object):
	def __init__(self, game_factory):
		self._game_sessions = {}
		self._rooms = []
		self._lock = asyncio.Lock()
		self._game_factory = game_factory

	def get_game_session(self, game_room, pause_timeout=10) -> GameSession:
		if game_room.room_name not in self._game_sessions:
			self._game_sessions[game_room.room_name] = GameSession(
				self._game_factory(),
				self,
				game_room,
				pause_timeout) # create new game logic for the game room.
		return self._game_sessions[game_room.room_name]

	def remove_session(self, session_id):
		if session_id in self._game_sessions:
			del self._game_sessions[session_id]

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

class GameConsumer(AsyncWebsocketConsumer):
	def __init__(self, game_server: GameServer, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._game_server = game_server
		self._game_session = None
		self.disconnected = False
		self._lost_connection = False

	async def send_json(self, data: dict):
		await self.send(text_data=json.dumps(data))

	async def state_callback(self, data):
		await self.channel_layer.group_send(
				self.room_name,
				{
					'type': 'game_state',
					'message': data
				}
			)

	async def connect(self):
		self.room_name = room_name = self.scope['url_route']['kwargs']['room_name']
		room_name = self.scope['url_route']['kwargs']['room_name']
		query_string = self.scope.get('query_string').decode('utf-8')
		params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
		token = params.get('token')
		csrf = params.get('csrf_token')

		if not token and not csrf:
			# If the room does not exist, close the connection
			await self.accept()
			await self.send_json({
				"type": "websocket.close",
				"code": 4000,  # Custom close code
				"reason": "Tokens are missing."
			})
			await self.close()
			return

		user = auth.get_user_with_token(token, csrf)
		if not user:
			# If the room does not exist, close the connection
			await self.accept()
			await self.send_json({
				"type": "websocket.close",
				"code": 4000,  # Custom close code
				"reason": "Invalid tokens."
			})
			self.close()
			return

		self.player_room = player_room = await get_player_room(user['user_id'], room_name)
		if not player_room:
			await self.accept()
			await self.send_json({
				"type": "websocket.close",
				"code": 4000,  # Custom close code
				"reason": "Player has no game room."
			})
			self.close()
			return

		self.game_room = await get_game_room(self.player_room)
		expected_players = await get_min_players(self.game_room)

		# create new game session if none exists.
		async with self._game_server as server:
			session = server.get_game_session(self.game_room)
			await self.channel_layer.group_add(self.room_name, self.channel_name)
			# if the amount of players is met, notify all clients.
			self.player = await get_player_position(player_room)
			session.current_players += 1
			session.set_player(self.player, await get_player_room_player(player_room))
			if session.current_players == expected_players:
				# keep a reference to the game session.
				self._game_session = session
				await self.accept()
				# send ready notification.
				await self.channel_layer.group_send(
				self.room_name,
				{
					'type': 'game_status',
					'message': {'status': 'ready'}
				})
				session.on_session_end(self.flush_game_session)
				session.on_connection_lost(self.connection_lost)
				# only start new game loop if no game is in session.
				if not await in_session(self.game_room):
					asyncio.create_task(self._game_session.start(self.state_callback))
					session.resume()
					await set_in_session(self.game_room, True)
					return
				# resume game in case it paused.
				session.resume()
			elif session.current_players < expected_players:
				session.on_session_end(self.flush_game_session)
				session.on_connection_lost(self.connection_lost)
				await self.accept()
				self._game_session = session
				await self.channel_layer.group_send(
				self.room_name,
				{
					'type': 'game_status',
					'message': {'status': 'waiting'}
				})

	async def flush_game_session(self, data):
		if data['player'] == self.player:
			data = {'type': 'end', 'status': 'win'}
		else:
			data = {'type': 'end', 'status': 'lost'}
		await self.send(text_data=json.dumps(data))
		await self.channel_layer.group_discard(self.room_name, self.channel_name)

	async def connection_lost(self):
		if not self.disconnected:
			# todo: also need to send that a player disconnected.
			await self.send_json({'type': 'end', 'status': 'win'})
			await self.close()
		self._lost_connection = True
		# todo: need to delete the game room...
		await self.channel_layer.group_discard(self.room_name, self.channel_name)

	# todo: notify the game loop to pause the game
	async def disconnect(self, close_code):
		async with self._game_server as server:
			session = server.get_game_session(self.game_room)
			# todo: if both players disconnected, end the game
			if session.current_players > 0:
				session.current_players -= 1
			session.remove_callback(
				'session-end',
				self.flush_game_session)
			session.pause()
			# todo: send a message to clients when a player disconnects.
			await self.channel_layer.group_discard(self.room_name, self.channel_name)
			self.disconnected = True

	# receives data from websocket.
	async def receive(self, bytes_data):
		if self.disconnected:
			return
		if self._game_session:
			await self._game_session.update(bytes_data, self.player)
		else:
			await self.channel_layer.group_send(
				self.room_name,
				{
					'type': 'game_state',
					'message': {'status': 'no session'}
				}
			)

	async def game_state(self, event):
		await self.send(text_data=json.dumps(event['message']))

	async def game_status(self, event):
		await self.send(text_data=json.dumps(event['message']))
