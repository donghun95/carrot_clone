import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import ChatRoom, ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        exists = await sync_to_async(ChatRoom.objects.filter(id=self.room_id).exists)()
        if not exists:
            await self.close()
            return
        
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close()
            return

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

    # ⬇⬇⬇ 여기부터 수정됨 ⬇⬇⬇
    @sync_to_async
    def get_room(self, room_id):
        return ChatRoom.objects.get(id=room_id)

    @sync_to_async
    def save_message(self, room, user, message):
        return ChatMessage.objects.create(
            room=room,
            sender=user,
            message=message
        )
    # ⬆⬆⬆ 여기까지 수정됨 ⬆⬆⬆

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        user = self.scope["user"]

        # 비동기 안전하게 ORM 호출
        room = await self.get_room(self.room_id)
        await self.save_message(room, user, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "username": user.username,
                "message": message
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "username": event["username"],
            "message": event["message"]
        }))