import os
import django
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from user_data.models import UserProfile

@database_sync_to_async
def set_player_online_status(user, status : bool):
    profile = UserProfile.objects.get(user=user)
    profile.online_status = status
    profile.save()

class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(f"WebSocket connection attempt from {self.scope['client']}", flush=True)
        if self.scope["user"].is_authenticated:
            self.user = self.scope["user"]
            print("Connecting user: ", self.user.id, flush=True)
            await set_player_online_status(self.user, True)
            await self.accept()
            await self.channel_layer.group_add(f"user_{self.user.id}", self.channel_name)
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.scope["user"].is_authenticated:
            print("Disconnecting user: ", self.user.id, flush=True)
            print("Close code: ", close_code, flush=True)
            await set_player_online_status(self.user, False)
            await self.channel_layer.group_discard(f"user_{self.user.id}", self.channel_name)

    async def user_logout(self, event):
        print(f"Logging out user {self.user.id} via channels", flush=True)
        await self.close()