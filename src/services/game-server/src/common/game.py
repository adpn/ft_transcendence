import json
import abc
import asyncio
import os
import django
import time
import urllib
import html


from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import BaseChannelLayer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from common import auth_client as auth
from common.models import UserChannel
from games.models import (
	Game,
	Player,
	PlayerRoom,
	GameResult,
	TournamentGameRoom,
	GameRoom,
	Tournament,
	TournamentParticipant)
from games.views import _join_tournament

@database_sync_to_async
def get_user_channel(user_id: str) -> UserChannel:
	return UserChannel.objects.filter(
		user_id=user_id
	).first()

@database_sync_to_async
def store_user_channel(user_id: str, channel_name):
	UserChannel(
		user_id=user_id,
		channel_name=channel_name).save()

@database_sync_to_async
def delete_user_channel(user_id: str, channel_name):
	UserChannel.objects.filter(
		user_id=user_id,
		channel_name=channel_name).delete()

@database_sync_to_async
def get_player_room(user_id: str, game_room: str, player_name="host") -> PlayerRoom:
	return PlayerRoom.objects.filter(
		player__player_name=player_name,
		player__user_id=user_id,
		game_room__room_name=game_room).first()

@database_sync_to_async
def leave_game_room(player: Player, game_room: GameRoom):
	PlayerRoom.objects.filter(player=player, game_room=game_room).first().delete()
	game_room.num_players -= 1
	game_room.save(update_fields=['num_players'])

@database_sync_to_async
def get_tournament_room_name(tournament_room: TournamentGameRoom) -> str:
	return tournament_room.game_room.room_name

@database_sync_to_async
def get_tournament_player_room(player: Player, rooms):
	return PlayerRoom.objects.filter(
		player=player, 
		game_room__in=rooms).first()

@database_sync_to_async
def get_player_room_player(player_room: PlayerRoom) -> Player:
	return player_room.player

@database_sync_to_async
def get_player_room_player_id(player_room: PlayerRoom) -> int:
	return player_room.player.player_id

@database_sync_to_async
def get_expected_players(player_room: PlayerRoom) -> int:
	return player_room.game_room.expected_players

@database_sync_to_async
def get_player_id(player_room: PlayerRoom) -> int:
	return player_room.player.player_id

@database_sync_to_async
def set_player_position(player_room: PlayerRoom, position: int) -> None:
	player_room.player_position = position
	player_room.save()

@database_sync_to_async
def get_player_position(player_room: PlayerRoom) -> int:
	return player_room.player_position

@database_sync_to_async
def get_player_game_room(player_room: PlayerRoom) -> GameRoom:
	return player_room.game_room

@database_sync_to_async
def get_game_room_game(game_room: GameRoom) -> Game:
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

@database_sync_to_async
def get_tournament_room(game_room: GameRoom) -> TournamentGameRoom:
	return TournamentGameRoom.objects.filter(game_room=game_room).first()

@database_sync_to_async
def get_tournament_room(game_room: GameRoom) -> TournamentGameRoom:
	return TournamentGameRoom.objects.filter(game_room=game_room).first()

@database_sync_to_async
def get_tournament_room_tournament(tournament_room: TournamentGameRoom) -> Tournament:
	return tournament_room.tournament

@database_sync_to_async
def get_remaining_participants(tournament: Tournament) -> int:
	return TournamentParticipant.objects.filter(status="PLAYING", tournament=tournament).count()

@database_sync_to_async
def qualify_player(player: Player, tournament: Tournament) -> None:
	participant = TournamentParticipant.objects.filter(player=player, tournament=tournament).first()
	participant.tournament_round += 1
	participant.save(update_fields=['tournament_round'])
	# creates or joins a room in the tournament.
	_join_tournament(tournament.game, player, tournament, participant)

@database_sync_to_async
def get_tournament_participant(player: Player, tournament: Tournament) -> None:
	return TournamentParticipant.objects.filter(
		player=player, tournament=tournament).first()

@database_sync_to_async
def eliminate_player(player: Player, tournament: Tournament) -> TournamentParticipant:
	participant = TournamentParticipant.objects.filter(player=player, tournament=tournament).first()
	participant.status = "ELIMINATED"
	participant.save(update_fields=["status"])
	return participant

@database_sync_to_async
def set_tournament_winner(player: Player, tournament: Tournament) -> TournamentParticipant:
	participant = TournamentParticipant.objects.filter(player=player, tournament=tournament).first()
	participant.status = "WINNER"
	participant.save(update_fields=["status"])
	return participant

@database_sync_to_async
def delete_tournament(tournament: Tournament) -> None:
	tournament.delete()

@database_sync_to_async
def close_tournament(tournament: Tournament) -> Tournament:
	tournament.closed = True
	tournament.save(update_fields=['closed'])

@database_sync_to_async
def tournament_is_closed(tournament: Tournament) -> bool:
	tournament = Tournament.objects.filter(tournament_id=tournament.tournament_id).first()
	return tournament.closed

@database_sync_to_async
def get_room_num_players(room: GameRoom) -> int:
	return room.num_players

@database_sync_to_async
def get_tournament_room_tournament_id(tournament_room: TournamentGameRoom) -> str:
	return tournament_room.tournament.tournament_id

@database_sync_to_async
def get_game_room(room_name: str) -> GameRoom:
	return GameRoom.objects.filter(room_name=room_name).first()

@database_sync_to_async
def get_tournament(tournament_id: str) -> GameRoom:
	return Tournament.objects.filter(tournament_id=tournament_id).first()

@database_sync_to_async
def delete_guest_players(user_id: int) -> int:
	Player.objects.filter(is_guest=True, user_id=user_id).delete()

@database_sync_to_async
def close_game_room(game_room: GameRoom) -> None:
	game_room.closed = True
	game_room.save(update_fields=['closed'])

@database_sync_to_async
def get_participant_player(participant: TournamentParticipant):
	return participant.player

@database_sync_to_async
def remove_participant(tournament: Tournament, player: Player):
	TournamentParticipant.objects.filter(tournament=tournament, player=player).delete()

@database_sync_to_async
def update_tournament(tournament: Tournament, fields):
	tournament.save(update_fields=fields)

@database_sync_to_async
def player_at_position(room_name: str, position: int):
	return PlayerRoom.objects.filter(
		game_room__room_name=room_name,
		player_position=position).first().player

class GameSession(object):
	def __init__(self, game_logic, game_server, game_room, game_mode=None, pause_timeout=5):
		self._game_logic = game_logic
		self.current_players = 0
		self._game_room = game_room
		self._game_server = game_server
		self._session_id = game_room.room_name
		self._game_mode = game_mode
		self._end_callbacks = []
		self._connection_lost_callbacks = []
		self._pause_event = asyncio.Event()
		self._pause_event.set()
		self._timeout = pause_timeout
		self.is_running = True
		self._players = [None, None]
		self._game_result = GameResult()
		self._disconnected = False
		self._start_time = 0
		self._current_data = {
			"player": -1,
			"loser": -1,
			"score": [-1, -1]}

	def set_player(self, position, player):
		self._players[position] = player

	def get_player(self, position) -> Player:
		return self._players[position]

	async def update(self, data, player):
		await self._game_logic.update(data, player)

	async def start(self, callback):
		self._game_result.game = await get_game_room_game(self._game_room)
		await callback(await self._game_logic.startEvent())
		self._start_time = t0 = time.time()
		while self.is_running:
			await asyncio.gather(
				self.game_loop(callback),
				asyncio.sleep(0.03)) # about 30 loops/second
		self._game_result.game_duration = time.time() - t0
		# TODO: protect storage of result -> try catch
		if not self._disconnected:
			try:
				await store_game_result(self._game_result)
			except django.db.utils.IntegrityError:
				pass
		await delete_game_room(self._game_room)
		#self._game_server.remove_session(self._session_id)

	async def game_loop(self, callback):
		try:
			await asyncio.wait_for(self._pause_event.wait(), self._timeout)
		except asyncio.TimeoutError:
			for end in self._connection_lost_callbacks:
				self._current_data['score'] = self._game_logic.score
				self._game_result.game_duration = time.time() - self._start_time
				await end(
					self,
					self._game_mode,
					self._current_data,
					self._game_result)
			await set_in_session(self._game_room, False)
			self.is_running = False
			self._disconnected = True
			return
		self._current_data = data = await self._game_logic.gameTick()
		await callback(data)
		async for data in self._game_logic.sendEvent():
			if data["type"] == "win":
				self._game_server.remove_session(self._session_id)
				await set_in_session(self._game_room, False)
				self._game_result.winner = self._players[data["player"]]
				self._game_result.loser = self._players[data["loser"]]
				self._game_result.winner_score = data["score"][data["player"]]
				self._game_result.loser_score = data["score"][data["loser"]]
				#self._game_result.game = await get_game_room_game(self._game_room)
				if self._game_mode:
					data = await self._game_mode.handle_end_game(data, self._game_result)
				for end in self._end_callbacks:
					await end(data)
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

class QuickGameMode(object):
	def __init__(self, channel_layer: BaseChannelLayer) -> None:
		self.channel_layer = channel_layer
		self.game_room = None
		self.started = True

	async def ready(self, session: GameSession, room_name: str, game_room: GameRoom, state_callback) -> None:
		await self.channel_layer.group_send(
		room_name, {
			'type': 'game_status',
			'message': {
				'status': 'ready'
				}
		})
		self.game_room = game_room
		if not await in_session(game_room):
			asyncio.create_task(session.start(state_callback))
			session.resume()
			await set_in_session(game_room, True)
			return
		# resume game in case it paused.
		session.resume()

	async def handle_end_game(self, data, game_result):
		return data

	async def handle_disconnection(self, room_name, player: Player):
		game_room = await get_game_room(room_name)
		if not game_room:
			return
		# delete game room if not is session (means player canceled)
		if not await in_session(game_room):
			await delete_game_room(game_room)

	async def get_participants(self, user, game_room):
		player_rooms = PlayerRoom.objects.filter(
			game_room=game_room
		).order_by('player_position')
		result = []
		async for player_room in player_rooms:
			player = await get_player_room_player(player_room)
			result.append({
				'player_id': player.user_id,
				'player_position': player_room.player_position,
				'player_name': player.player_name if player.is_guest else player.user_name,
				'player_type': 'guest' if player.is_guest else 'host',
				'game_mode': 'quick-game'})
		return result

class TournamentMode(object):
	def __init__(self,
		tournament: Tournament,
		tournament_id,
		game_room,
		channel_name,
		channel_layer: BaseChannelLayer) -> None:
		self._tournament = tournament
		self.channel_layer = channel_layer
		self._channel_name = channel_name
		self._ready = False
		self._tournament_id = tournament_id
		self._game_room = game_room
		self.room_name = None
		self.started = False

	async def ready(self,
		session: GameSession,
		room_name: str,
		game_room: GameRoom,
		state_callback) -> None:
		if self.started:
			return
		closed = await tournament_is_closed(self._tournament)
		if not closed:
			await self.channel_layer.group_send(
				room_name,
				{
					'type': 'game_status',
					'message': {
						'status': 'waiting'
						}
				})
			return
		self._game_room = game_room = await get_game_room(room_name)
		if not game_room:
			return
		await self.channel_layer.group_send(
			room_name,
			{
				'type': 'game_status',
				'message': {
					'status': 'ready'
					}
			})
		if not await in_session(game_room):
			asyncio.create_task(session.start(state_callback))
			session.resume()
			await set_in_session(game_room, True)
			return
		# resume game in case it paused.
		session.resume()

	async def handle_end_game(self, data: dict, game_result: GameResult):
		tournament = await get_tournament(self._tournament_id)
		await eliminate_player(game_result.loser, tournament)
		remaining_players = await get_remaining_participants(tournament)
		if remaining_players == 1:
			await delete_tournament(tournament)
			data["type"] = "win"
			return data
		await close_game_room(self._game_room)
		await qualify_player(game_result.winner, tournament)
		data["type"] = "round"
		return data

	async def handle_disconnection(self, room_name, player: Player):
		# TODO: if the tournament is not closed, delete the player and decrement the
		# number of participants.
		await self.channel_layer.group_discard(
			self._tournament_id,
			self._channel_name)
		# delete game room if not is session (means player canceled)
		tournament = await get_tournament(self._tournament_id)
		if not tournament:
			return
		if not await tournament_is_closed(tournament):
			game_room = await get_game_room(room_name)
			if game_room:
				await leave_game_room(player, game_room)
				if await get_room_num_players(game_room) <= 0:
					await delete_game_room(game_room)
			tournament.participants -= 1
			if player:
				await remove_participant(tournament, player)
			if tournament.participants == 0:
				await delete_tournament(tournament)
			else:
				await update_tournament(tournament, ['participants'])


	async def get_participants(self, user, game_room):
		participants = TournamentParticipant.objects.filter(
			tournament=self._tournament).order_by('tournament_position')
		result = []
		rooms = TournamentGameRoom.objects.filter(
			tournament=self._tournament).values_list('game_room', flat=True)
		async for participant in participants:
			player = await get_participant_player(participant)
			# look for the player room. TODO: need a better query for this.
			player_room = await get_tournament_player_room(player, rooms)
			if not player_room:
				continue
			result.append({
				'user_id': player.user_id,
				'player_name': player.player_name if player.is_guest else player.user_name,
				'player_type': 'guest' if player.is_guest else 'host',
				'player_position': player_room.player_position,
				'player_status': participant.status.lower(),
				'game_mode': 'tournament'})
		return result

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

class LocalMode(object):
	def __init__(self,
		game_server: GameServer,
		player_ids: list,
		room_name: str,
		host_user_id: str,
		channel_layer: BaseChannelLayer,
		consumer: AsyncWebsocketConsumer) -> None:

		self._player_ids = player_ids
		self._game_server = game_server
		self.channel_layer = channel_layer
		self.consumer = consumer
		self.room_name = room_name
		self.game_room = None
		self._player_room = None
		self._loaded = False
		self._players_positions = [0, 1]
		self._host_user_id = int(host_user_id)
		self._game_session = None
		self._disconnected = False
		self._player_rooms = [None, None]

	async def _load_players(self):
		self._player_rooms[0] = player1_room = await get_player_room(
			self._host_user_id,
			self.room_name,
			self._player_ids[0])
		if not player1_room:
			return False
		self._player_rooms[1] = player2_room = await get_player_room(
			self._host_user_id,
			self.room_name,
			self._player_ids[1])
		if not player2_room:
			return False
		self._loaded = True
		return self._loaded

	async def validate_player(self):
		if not await self._load_players():
			return False
		return True

	async def get_game_room(self):
		if not self._player_room:
			self._player_room = await get_player_room(
				self._host_user_id,
				self.room_name,
				self._player_ids[0])
		self.game_room = await get_player_game_room(self._player_room)
		return self.game_room

	async def state_callback(self, data):
		await self.channel_layer.group_send(
				self.room_name,
				{
					'type': 'game_state',
					'message': data
				})

	async def start_session(self, game_mode, state_callback):
		if not self._loaded:
			await self._load_players()
		async with self._game_server as server:
			if not self.game_room:
				self.game_room = await self.get_game_room()
			session = server.get_game_session(self.game_room, game_mode)
			session.current_players = 2
			for i, player_room in enumerate(self._player_rooms):
				position = await get_player_position(player_room)
				session.set_player(
					position,
					await get_player_room_player(player_room))
				self._players_positions[i] = position
			session.on_session_end(self.flush_game_session)
			session.on_connection_lost(self.connection_lost)
			self._game_session = session
			await self.consumer.accept()
			await game_mode.ready(
				session, self.room_name,
				self.game_room, state_callback)

	async def update(self, bytes_data):
		if self._disconnected:
			return
		session = self._game_session
		# update for the given position.
		await session.update(
			bytes_data,
			self._players_positions[int(bytes_data[3])])

	# in local mode there is no waiting time.
	async def tournament_message(self, event, game_mode):
		pass

	async def flush_game_session(self, data):
		# just send the winner to client in local mode.
		for position in self._players_positions:
			player = await get_player_room_player(self._player_rooms[position])
			if data['player'] == position:
				data = {
					'type': 'end',
					'context': data['type'],
					'status': 'win',
					'winner': position,
					'player_name': player.player_name if player.is_guest else player.user_name,
					'player_id': player.user_id
					}
				await self.consumer.send(text_data=json.dumps(data))
				break

	async def connection_lost(self, game_mode, session: GameSession):
		pass

	async def disconnect(self, game_mode):
		self._loaded = False
		self._disconnected = True
		async with self._game_server as server:
			game_room = await get_game_room(self.room_name)
			if game_room:
				session = server.get_game_session(game_room, game_mode)
				# todo: if both players disconnected, end the game
				session.remove_callback(
					'session-end',
					self.flush_game_session)
				server.remove_session(session._session_id)
				await delete_game_room(game_room)
			await delete_guest_players(self._host_user_id)
			await self.channel_layer.group_discard(self.room_name, self.consumer.channel_name)

class OnlineMode(object):
	def __init__(self,
		game_server: GameServer,
		user: dict,
		room_name: str,
		channel_layer: BaseChannelLayer,
		consumer: AsyncWebsocketConsumer) -> None:

		self._game_server = game_server
		self._player_room = None
		self._user = user
		self.game_room = None
		self.room_name = room_name
		self.channel_layer = channel_layer
		self.consumer = consumer
		self._lost_connection = False
		self._disconnected = False
		self.player_position = 0

	async def validate_player(self):
		if not self._player_room:
			self._player_room = player_room = await get_player_room(
				self._user['user_id'],
				self.room_name)
			if not player_room:
				return False
		return True

	async def get_game_room(self):
		if not self._player_room:
			self._player_room = await get_player_room(
				self._user['user_id'],
				self.room_name)
		self.game_room = await get_player_game_room(self._player_room)
		return self.game_room

	async def state_callback(self, data):
		await self.channel_layer.group_send(
			self.room_name, {
				'type': 'game_state',
				'message': data
			})

	async def start_session(self, game_mode, state_callback):
		player_room = self._player_room
		if not player_room:
			await self.get_game_room()
		expected_players = await get_min_players(self.game_room)
		async with self._game_server as server:
			session = server.get_game_session(self.game_room, game_mode)
			# if the amount of players is met, notify all clients.
			self.player_position = await get_player_position(player_room)
			self.player = await get_player_room_player(player_room)
			# if session.get_player(self.player_position):
			# 	pass
			session.current_players += 1
			session.set_player(
				self.player_position,
				await get_player_room_player(player_room)) # ! don't optimize this
			# TODO: also check against num_players in the game room
			# (if it is one, there is an issue)
			session.on_session_end(self.flush_game_session)
			session.on_connection_lost(self.connection_lost)
			self._game_session = session
			if session.current_players == expected_players:
				await self.consumer.accept()
				await game_mode.ready(
					session, self.room_name,
					self.game_room, state_callback)
			elif session.current_players < expected_players:
				await self.consumer.accept()
				await self.channel_layer.group_send(
				self.room_name,
				{
					'type': 'game_status',
					'message': {
						'status': 'waiting'
						}
				})

	async def update(self, bytes_data):
		if self._disconnected:
			return
		if self._game_session:
			await self._game_session.update(bytes_data, self.player_position)
		else:
			await self.channel_layer.group_send(
				self.room_name,
				{
					'type': 'game_state',
					'message': {'status': 'no session'}
				})

	# in local mode there is no waiting time.
	async def tournament_message(self, event, game_mode):
		# attempt to launch tournament.
		if not self._game_session:
			return
		if not game_mode.started:
			async with self._game_server:
				await game_mode.ready(
					self._game_session,
					self.room_name,
					self.game_room,
					self.state_callback)

	async def flush_game_session(self, data):
		if data['player'] == self.player_position:
			data = {
				'type': 'end',
				'context': data['type'],
				'status': 'win',
				'winner': self.player_position,
				'player_name': self.player.player_name if self.player.is_guest else self.player.user_name,
				'player_id': self.player.user_id
				}
		else:
			player = await player_at_position(self.room_name, 1 - self.player_position)
			data = {
				'type': 'end',
				'context': data['type'],
				'status': 'lost',
				'winner': 1 - self.player_position,
				'player_name': player.player_name if player.is_guest else player.user_name,
				'player_id': player.user_id
				}
		await self.consumer.send(text_data=json.dumps(data))
		await self.channel_layer.group_discard(
			self.room_name, self.consumer.channel_name)
		await self.consumer.close()

	async def connection_lost(self, session: GameSession, game_mode, data: dict, game_result: GameResult):
		if not self._disconnected:
			# if did not disconnect then it is the winner.
			winner_index = self.player_position
			loser_index = 1 - self.player_position
			game_result.winner = session.get_player(winner_index)
			game_result.loser = session.get_player(loser_index)
			game_result.winner_score = data["score"][winner_index]
			game_result.loser_score = data["score"][loser_index]
			data = await game_mode.handle_end_game(data, game_result)
			data['reason'] = 'disconnection'
			data['player'] = self.player_position
			# the remaining player stores the game_result
			await store_game_result(game_result)
			await self.flush_game_session(data)
			self._lost_connection = True
			return

	async def disconnect(self, game_mode):
		async with self._game_server as server:
			if self.game_room:
				session = server.get_game_session(self.game_room, game_mode)
				# todo: if both players disconnected, end the game
				if session.current_players > 0:
					session.current_players -= 1
				session.remove_callback(
					'session-end',
					self.flush_game_session)
				session.pause()
			# todo: send a message to clients when a player disconnects.
			await self.channel_layer.group_discard(self.room_name, self.consumer.channel_name)
			if game_mode:
				await game_mode.handle_disconnection(
					self.room_name,
					session.get_player(self.player_position))
			self._disconnected = True
			# delete game room if it is not in session.

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
		# check if the game room is in a tournament room.
		tournament_room = await get_tournament_room(self.game_room)
		if tournament_room:
			# add channel to tournament group.
			tournament_id = await get_tournament_room_tournament_id(tournament_room)
			self._game_mode = game_mode = TournamentMode(
				await get_tournament_room_tournament(tournament_room),
				tournament_id,
				self.game_room,
				self.channel_name,
				self.channel_layer
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
			self._game_mode = game_mode = QuickGameMode(self.channel_layer)
		await self.channel_layer.group_add(self.room_name, self.channel_name)
		# send participants to clients.
		await self.channel_layer.group_send(
			self.room_name,
			{
				'type': 'tournament_message',
				'message': {
					'type': 'participants',
					'values': await self._game_mode.get_participants(
						user,
						self.game_room)
				}
			})

		await game_locality.start_session(
			game_mode,
			self.state_callback)

	# todo: notify the game loop to pause the game
	async def disconnect(self, close_code):
		# await delete_user_channel(self.user['user_id'], self.channel_name)
		if not self.game_room:
			return
		await self._game_locality.disconnect(self._game_mode)

	# receives data from websocket.
	async def receive(self, bytes_data):
		await self._game_locality.update(bytes_data)

	async def game_state(self, event):
		if event['message']['type'] == 'participants':
			print("PARTICIPANTS", event['message'], flush=True)
		await self.send(text_data=json.dumps(event['message']))

	async def game_status(self, event):
		await self.send(text_data=json.dumps(event['message']))

	async def tournament_message(self, event):
		if (event['message']['type'] == 'participants'):
			await self.game_status(event)
			return
		await self._game_locality.tournament_message(
			event, self._game_mode)
