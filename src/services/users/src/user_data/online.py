import os
import django
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
# from authentication.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from user_data.models import UserProfile

class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(f"WebSocket connection attempt from {self.scope['client']}", flush=True)
        if self.scope["user"].is_authenticated:
            self.user = self.scope["user"]
            print("Connecting user: ", self.user.username, flush=True)
            await self.mark_online(self.user)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.scope["user"].is_authenticated:
            print("Disconnecting user: ", self.user.username, flush=True)
            await self.mark_offline(self.scope["user"])

    @staticmethod
    async def mark_online(user):
        profile = await sync_to_async(UserProfile.objects.get)(user=user)
        profile.online_status = True
        await sync_to_async(profile.save)()

    @staticmethod
    async def mark_offline(user):
        profile = await sync_to_async(UserProfile.objects.get)(user=user)
        profile.online_status = False
        await sync_to_async(profile.save)()
