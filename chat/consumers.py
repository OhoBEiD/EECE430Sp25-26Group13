import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        self.room_group_name = f'chat_{self.thread_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        has_access = await self.check_access(self.thread_id, self.user)
        if not has_access:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        
        msg_obj = await self.save_message(self.thread_id, self.user, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username,
                'timestamp': msg_obj.timestamp.isoformat(),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def check_access(self, thread_id, user):
        from .models import ChatThread
        from accounts.roles import role_of, Role
        from accounts.querysets import teams_for
        
        try:
            thread = ChatThread.objects.get(id=thread_id)
        except ChatThread.DoesNotExist:
            return False
            
        allowed_teams_qs = teams_for(user)
        if thread.thread_type in ['team_general', 'team_staff']:
            if not allowed_teams_qs.filter(id=thread.team_id).exists():
                return False
            if thread.thread_type == 'team_staff' and role_of(user) not in [Role.COACH, Role.MANAGER, Role.ADMIN]:
                return False
        elif thread.thread_type == 'event':
            if not allowed_teams_qs.filter(id=thread.event.team_id).exists():
                return False
        return True

    @database_sync_to_async
    def save_message(self, thread_id, user, text):
        from .models import ChatMessage
        return ChatMessage.objects.create(thread_id=thread_id, sender=user, text=text)
