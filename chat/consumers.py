from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
import json
import re
from .models import Message, Group, BadWord


class ChatConsumer(AsyncWebsocketConsumer):
    @sync_to_async
    def get_sender(self, message):
        return ("(Admin) " if message.is_admin else "") + message.sender.username
    
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope["user"]
        self.is_admin = self.user.is_staff
        self.recipient = await sync_to_async(Group.objects.get)(name=self.room_name)
        self.bad_words = await database_sync_to_async(BadWord.objects.values_list)('word', flat=True)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        recipient = await database_sync_to_async(Group.objects.get)(name=self.room_name)
        messages = await database_sync_to_async(Message.objects.filter)(recipient=recipient)
        if await sync_to_async(list)(messages):
            for message in messages:
                await self.send(
                    text_data=json.dumps({"message": await self.get_sender(message) + ": " + message.content, 'is_admin': message.is_admin})
                )


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json["message"].strip():
            bad_words = await sync_to_async(list)(self.bad_words)
            for bad_word in bad_words:
                bad_word_len = len(bad_word)
                bad_word_re = r'\b' + bad_word + r'\b'
                res = [m.start() for m in re.finditer(bad_word_re, text_data_json['message'])]
                for index in res:
                    text_data_json["message"] = text_data_json["message"][:index] + "*"*bad_word_len + text_data_json["message"][index+bad_word_len:]

            message_object = await sync_to_async(Message.objects.create)(sender=self.user, recipient=self.recipient, content=text_data_json["message"])

            message = str(self.user) + ": " + text_data_json["message"]

            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.message", "message": message, 'is_admin': message_object.is_admin}
            )


    async def chat_message(self, event):
        message = event["message"]
        is_admin = event["is_admin"]
        await self.send(text_data=json.dumps({"message": message, 'is_admin': is_admin}))
