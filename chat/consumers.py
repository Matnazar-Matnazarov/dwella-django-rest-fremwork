# Dwella/chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Chat
from connect_announcements.models import ConnectAnnouncement
from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
import base64
import uuid

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return

        self.connect_announcement_id = self.scope['url_route']['kwargs']['connect_announcement_id']
        self.master_id = self.scope['url_route']['kwargs']['master_id']
        self.client_id = self.scope['url_route']['kwargs']['client_id']

        # Foydalanuvchi haqiqatan ham master yoki client ekanligini tekshirish
        if str(self.user.id) not in [str(self.master_id), str(self.client_id)]:
            await self.close()
            return

        # Guruh nomi har doim bir xil bo‘lishi uchun
        user_ids = sorted([str(self.master_id), str(self.client_id)])
        self.room_group_name = f"chat_{self.connect_announcement_id}_{user_ids[0]}_{user_ids[1]}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        image_data = data.get('image', None)
        chat = await self.save_message(message, image_data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'image': chat.image.url if chat.image else None,
                'sender_id': str(self.user.id),
                'sender_username': self.user.username,
                'timestamp': chat.created_at.isoformat(),
                'chat_id': str(chat.id)
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'image': event['image'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'timestamp': event['timestamp'],
            'chat_id': event['chat_id']
        }))

    @database_sync_to_async
    def save_message(self, message, image_data=None):
        connect_announcement = ConnectAnnouncement.objects.get(id=self.connect_announcement_id)
        master = User.objects.get(id=self.master_id)
        client = User.objects.get(id=self.client_id)
        chat = Chat(
            message=message,
            connect_announcement=connect_announcement,
            master=master,
            client=client
        )
        if image_data and "base64," in image_data:
            format, imgstr = image_data.split('base64,')
            ext = format.split('/')[-1].split(';')[0]
            file_name = f"{uuid.uuid4()}.{ext}"
            data = ContentFile(base64.b64decode(imgstr), name=file_name)
            chat.image = data
        chat.save()
        return chat