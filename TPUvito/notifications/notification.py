from channels.exceptions import DenyConnection
from channels.layers import get_channel_layer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.apps import apps
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from django.db.models.signals import m2m_changed
from django.contrib.auth.models import AnonymousUser
from django.dispatch import receiver
User = get_user_model()
Notification = apps.get_model('users','Notification')
users_online = []
class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user']==AnonymousUser:
            DenyConnection('login or register')
        await self.accept()
        self.user_id = self.scope['user'].id
        users_online.append(self.user_id)
        self.room_name = f'notify-user-{self.user_id}'
        await self.channel_layer.group_add(self.room_name,self.channel_name)
        await self.send_json({"type":"connect","status":"success"})
    @staticmethod
    @receiver(m2m_changed,sender=User.notifications.through)
    async def get_notify(instance,action,**kwargs):
        if action=="post_add":
            model = await instance.notifications.alast()
            layer = get_channel_layer()
            if instance.id in users_online:
                await layer.group_send(f'notify-user-{instance.id}',{'type':'send.notify','data':{'type':'notify','id':model.id,'head':model.Head,'body':model.Body,'timestamp':model.Timestamp.strftime('%m/%d/%Y, %H:%M:%S')}})
    async def send_notify(self,event):
        await self.send_json(event['data'])
    async def disconnect(self, code):
            users_online.remove(self.scope['user'].id)

    
    