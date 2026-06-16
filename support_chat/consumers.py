import json
from datetime import datetime

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.utils import timezone
from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.room_name = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()

        # Signal présence en ligne
        await self.set_online(True)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_status",
                "user_id": self.user.id,
                "is_online": True,
                "username": self.user.username,
            },
        )

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            # Signal hors ligne
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_status",
                    "user_id": self.user.id,
                    "is_online": False,
                    "username": self.user.username,
                },
            )
            await self.set_online(False)
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )

    @sync_to_async
    def set_online(self, online):
        try:
            user = self.user.__class__.objects.get(pk=self.user.pk)
            user.is_online = online
            user.last_seen = timezone.now() if not online else user.last_seen
            user.save(update_fields=["is_online", "last_seen"])
        except Exception:
            pass

    @sync_to_async
    def save_message(self, room_id, user, content):
        try:
            conv = Conversation.objects.get(id=room_id)
            return Message.objects.create(
                conversation=conv,
                sender=user,
                content=content,
            )
        except Conversation.DoesNotExist:
            return None

    @sync_to_async
    def get_online_users(self, room_id):
        try:
            conv = Conversation.objects.select_related(
                "client", "agent"
            ).get(id=room_id)
            result = {}
            if conv.client:
                result[conv.client.id] = {
                    "is_online": conv.client.is_online,
                    "username": conv.client.username,
                }
            if conv.agent:
                result[conv.agent.id] = {
                    "is_online": conv.agent.is_online,
                    "username": conv.agent.username,
                }
            return result
        except Conversation.DoesNotExist:
            return {}

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get("type", "message")

        if msg_type == "typing":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_typing",
                    "user_id": self.user.id,
                    "username": self.user.username,
                    "is_typing": data.get("is_typing", True),
                },
            )
            return

        if msg_type == "status":
            # Demande de statut de présence
            online_users = await self.get_online_users(self.room_name)
            await self.send(text_data=json.dumps({
                "type": "online_status",
                "users": online_users,
            }))
            return

        # Message normal
        message_content = data.get("message", "")
        if not message_content:
            return

        saved_msg = await self.save_message(
            self.room_name, self.user, message_content
        )

        if saved_msg:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message_content,
                    "sender_id": self.user.id,
                    "sender_username": self.user.username,
                    "time": saved_msg.sent_at.strftime("%H:%M"),
                },
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "message",
            "message": event["message"],
            "sender_id": event["sender_id"],
            "sender_username": event.get("sender_username", ""),
            "time": event.get("time", ""),
        }))

    async def user_typing(self, event):
        if event["user_id"] != self.user.id:
            await self.send(text_data=json.dumps({
                "type": "typing",
                "user_id": event["user_id"],
                "username": event["username"],
                "is_typing": event["is_typing"],
            }))

    async def user_status(self, event):
        if event["user_id"] != self.user.id:
            await self.send(text_data=json.dumps({
                "type": "user_status",
                "user_id": event["user_id"],
                "is_online": event["is_online"],
                "username": event.get("username", ""),
            }))
