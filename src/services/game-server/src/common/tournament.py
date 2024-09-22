import json
import abc
import asyncio
import os
import django
import time

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

class TournamentConsumer(AsyncWebsocketConsumer):
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

	#TODO: BUG when the same player joins the from two windows it still works ???
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