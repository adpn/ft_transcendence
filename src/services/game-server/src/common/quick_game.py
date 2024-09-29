import asyncio

from channels.layers import BaseChannelLayer

from games.models import (
	Player,
	PlayerRoom,
	GameRoom)

from common.game_session import GameSession
from common.db_utils import (
	in_session,
	set_in_session,
	get_game_room,
	delete_game_room,
	get_player_room_player
)

class QuickGameMode(object):
	def __init__(
			self, 
			channel_layer: BaseChannelLayer,
			game_locality) -> None:
		self.channel_layer = channel_layer
		self.started = True
		self.game_locality = game_locality
		self.tournament = None

	async def ready(self, 
				 session: GameSession, 
				 room_name: str, 
				 game_room: GameRoom, 
				 state_callback) -> None:
		await self.channel_layer.group_send(
		room_name, {
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

	async def handle_end_game(self, data, consumers, game_result):
		if data['type'] == 'win':
			for consumer in consumers:
				await consumer.cleanup_data()
		return data
	
	async def cleanup_data(self, consumers, room_name, players):
		for consumer in consumers:
			await consumer.cleanup_data()
		game_room = await get_game_room(room_name)
		if not game_room:
			return
		await delete_game_room(game_room)

	async def handle_disconnection(self, channel_name, channel_layer, room_name, player: Player):
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

	async def get_room_players(self, user, game_room):
		await self.get_participants(user, game_room)
