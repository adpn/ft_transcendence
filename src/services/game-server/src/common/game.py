import json
import abc

from channels.generic.websocket import AsyncWebsocketConsumer

class GameLogic(abc.ABC):
	@abc.abstractclassmethod
	def update(data):
		pass

class GameServer(AsyncWebsocketConsumer):
	def __init__(self, game_logic, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._game_logic = game_logic

	async def connect(self):
		self.game_room = self.scope['url_route']['kwargs']['room_name']
		await self.channel_layer.group_add(self.game_room, self.channel_name)
		await self.accept()

	async def disconnect(self, close_code):
		await self.channel_layer.group_discard(self.game_room, self.channel_name)

	# receives data from websocket.
	async def receive(self, text_data):
		data = json.loads(text_data)
		# Handle received data here
		# Broadcast to group
		await self.channel_layer.group_send(
			self.game_room,
			{
				'type': 'game_message',
				'message': self._game_logic.update(data),
			}
		)

	async def game_message(self, event):
		await self.send(text_data=json.dumps(event['message']))
