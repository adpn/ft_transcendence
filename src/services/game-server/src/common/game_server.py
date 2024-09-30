import json
import asyncio
import os
import django
import urllib
import html


from channels.generic.websocket import AsyncWebsocketConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from common import auth_client as auth
from common.db_utils import (
	get_tournament_room,
	get_tournament_room_tournament_id,
	get_tournament_room_tournament,
	get_user_channel,
	store_user_channel,
	delete_user_channel
)

from common.game_session import GameSession
from common.local_game import LocalMode
from common.online_game import OnlineMode
from common.tournament_mode import TournamentMode
from common.quick_game import QuickGameMode

class GameServer(object):
	def __init__(self, game_factory):
		self._game_sessions = {}
		self._rooms = []
		self._lock = asyncio.Lock()
		self._game_factory = game_factory

	def get_game_session(self, game_room, game_mode, pause_timeout=10) -> GameSession:
		if not game_room:
			return
		if game_room.room_name not in self._game_sessions:
			self._game_sessions[game_room.room_name] = GameSession(
				self._game_factory(),
				self,
				game_room,
				game_mode,
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

class GameConsumer(AsyncWebsocketConsumer):
	def __init__(self, game_server: GameServer, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._game_server = game_server
		self._game_session = None
		self._disconnected = False
		self._lost_connection = False

		self._game_mode = None
		self.game_room = None

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
	'''
	TODO: BUG when the same player joins the game from two windows it still works
	(the same player gets in the session twice) !!!
	'''

	async def connect(self):

		self.room_name = room_name = self.scope['url_route']['kwargs']['room_name']
		query_string = self.scope.get('query_string').decode('utf-8')
		params = urllib.parse.parse_qs(query_string)
		token = params.get('token', [''])[0]  # Use the first element if available
		csrf = params.get('csrf_token', [''])[0]
		token = html.escape(token)
		csrf = html.escape(csrf)

		if not token and not csrf:
			print("NOT TOKEN!!!", flush=True)
			await self.accept()
			await self.send_json({
				"type": "websocket.close",
				"code": 4000,  # Custom close code
				"reason": "Tokens are missing."
			})
			await self.close()
			return

		self.user = user = auth.get_user_with_token(token, csrf)
		if not user:
			print("NOT USER!!!", flush=True)
			await self.accept()
			await self.send_json({
				"type": "websocket.close",
				"code": 4000,  # Custom close code
				"reason": "Invalid tokens."
			})
			await self.close()
			return

		# if await get_user_channel(user['user_id']):
		# 	print("ALREADY CONNECTED", flush=True)
		# 	# If a connection still exists, refuse the new connection
		# 	await self.accept()
		# 	await self.send_json({
		# 		"type": "websocket.close",
		# 		"code": 4000,  # Custom close code
		# 		"reason": "Already connected"
		# 	})
		# 	await self.close()
		# 	return

		# await store_user_channel(user['user_id'], self.channel_name)

		# create game locality mode.
		if params.get('local'):
			player1 = params.get('player1', [''])[0]
			player2 = params.get('player2', [''])[0]
			if player1 == player2:
				print("NOT LOCAL!!!", flush=True)
				await self.accept()
				await self.send_json({
					"type": "websocket.close",
					"code": 4000,  # Custom close code
					"reason": "Invalid player names!"
				})
				await self.close()
				return
			self._game_locality = game_locality = LocalMode(
				self._game_server,
				[player1, player2],
				room_name,
				user['user_id'],
				self.channel_layer,
				self)
		else:
			self._game_locality = game_locality = OnlineMode(
				self._game_server, user,
				room_name, self.channel_layer,
				self)
		'''
		TODO:
		check if the game room is in local mode if so, the game should start right away.
		the opponent should already be present in the game room (after calling the api)
		the connection request should contain the two guest players.

		TODO:
		in local mode need to retreive the rooms of the two guest players.
		'''

		if not await game_locality.validate_player():
			print("INVALID PLAYER!!!", flush=True)
			await self.accept()
			await self.send_json({
				"type": "websocket.close",
				"code": 4000,  # Custom close code
				"reason": "Player has no game room."
			})
			await self.close()
			return

		self.game_room = await game_locality.get_game_room()
		if not self.game_room:
			await self.accept()
			await self.send_json({
				"type": "websocket.close",
				"code": 4000,  # Custom close code
				"reason": "Game Room does not exist"
			})
			await self.close()
			return
		# check if the game room is in a tournament room.
		tournament_room = await get_tournament_room(self.game_room)
		if tournament_room:
			# add channel to tournament group.
			self.tournament_id = tournament_id = await get_tournament_room_tournament_id(
				tournament_room)
			tournament = await get_tournament_room_tournament(tournament_room)
			if not tournament:
				await self.accept()
				await self.send_json({
					"type": "websocket.close",
					"code": 4000,  # Custom close code
					"reason": "Tournament does not exist"
				})
				await self.close()
				return
			self._game_mode = game_mode = TournamentMode(
				tournament,
				tournament_id,
				self.game_room,
				self.channel_name,
				self.channel_layer,
				game_locality
			)
			# notify all consumers that there is a new participant.
			await self.channel_layer.group_send(
				tournament_id,
				{
					'type': 'tournament_message',
					'message': {
						'type': 'participant'
					}
				}
			)
			# add this channel to the group.
			await self.channel_layer.group_add(
				tournament_id,
				self.channel_name
			)
		else:
			self.tournament_id = tournament_id = self.room_name
			self._game_mode = game_mode = QuickGameMode(
				self.channel_layer, 
				game_locality)
		await self.channel_layer.group_add(
			self.room_name, self.channel_name)
		game_locality.game_mode = game_mode
		await self.accept()
		# send participants to clients.
		await self.broadcast_room_players()
		await self.broadcast_participants()
		await game_locality.start_session(
			game_mode,
			self.state_callback)

	# todo: notify the game loop to pause the game
	async def disconnect(self, close_code):
		# await delete_user_channel(self.user['user_id'], self.channel_name)
		if not self.game_room:
			return
		await self._game_locality.disconnect(
			self.channel_name, 
			self.channel_layer, self._game_mode)

	async def broadcast_participants(self):
		await self.channel_layer.group_send(
			self.tournament_id, {
				'type': 'tournament_message',
				'message': {
					'type': 'tournament.players',
					'values': await self._game_mode.get_participants(
						self.user,
						self.game_room)}})
	
	async def broadcast_room_players(self):
		players = await self._game_mode.get_room_players(
						self.user,
						self.game_room)
		await self.channel_layer.group_send(
			self.room_name, {
				'type': 'game_state',
				'message': {
					'type': 'room.players',
					'values': await self._game_mode.get_room_players(
						self.user,
						self.game_room)
						}})

	# receives data from websocket.
	async def receive(self, bytes_data):
		await self._game_locality.update(bytes_data)

	async def game_state(self, event):
		await self.send(text_data=json.dumps(event['message']))

	async def game_status(self, event):
		await self.send(text_data=json.dumps(event['message']))

	async def tournament_message(self, event):
		if event['message']['type'] == 'tournament.players':
			await self.game_status(event)
			return
		await self._game_locality.tournament_message(
			event, self._game_mode)
