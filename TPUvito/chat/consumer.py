

import datetime
from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.db.models import Q
from asgiref.sync import sync_to_async
from webpush import send_user_notification
import os
from ..settings import MEDIA_ROOT
from django.urls import reverse
User = get_user_model(
)
Notification = apps.get_model('users','Notification')
Chat = apps.get_model('TPUvito',"Chat")
Message = apps.get_model('TPUvito',"Message")
users_online = {}
class ChatConsumer(AsyncJsonWebsocketConsumer):
    @database_sync_to_async
    def get_all_chats(self,user):
         id = user.id
         chats = [chat for chat in Chat.objects.filter(Q(First_user=id)|Q(Second_user=id))]
         id = [chat.id for chat in chats]
         return chats,id
    @database_sync_to_async
    def get_messages(self,count,id):
        this_chat =Chat.objects.get(id=id) 
        return this_chat.Message.order_by("-timestamp")[count*20:20*(count+1)]
    @database_sync_to_async
    def get_second_user(self,this_chat,from_user):
        to_user = this_chat.Second_user if from_user==this_chat.First_user else this_chat.First_user 
        return to_user
    @database_sync_to_async
    def get_count_of_unreaded_messages(self):
        chat = Chat.objects.filter((Q(First_user=self.scope['user'].id)|Q(Second_user=self.to_user.id))&(Q(Second_user=self.scope['user'].id)|Q(First_user=self.to_user.id)))
        messages = [i.Messages.filter(author=self.to_user,read=False).count for i in chat]
        return messages
    async def connect(self):
        if self.scope['user']==AnonymousUser:
                    raise DenyConnection("Register or login")
        await self.accept()
        await self.channel_layer.group_add(f"user-{self.scope['user'].id}",self.channel_name)
        users_online[self.scope['user']]=self.channel_name 
    async def disconnect(self, close_code):
        users_online.pop(self.channel_name,False)
        await self.channel_layer.group_discard(f"user-{self.scope['user'].id}",self.channel_name)
        pass
    async def receive_json(self, content):
        data=content
        request_type = data["request_type"]
        if request_type=="send":
            message = data['message']
            try:
                to_user = await User.objects.aget(username=data["to_user"])
            except User.DoesNotExist:
                 print("ОШИБКА НЕ НАЙДЕН ПОЛЬЗОВАТЕЛЬ!:"+str(data["to_user"]))
                 return "ошибка, не нашли юзера"
            from_user = self.scope['user']
            this_chat=None
            try:
                this_chat = await Chat.objects.aget((Q(First_user__id=self.scope['user'].id)&Q(Second_user__id=to_user.id)&Q(adv__id=data['adv_id']))|(Q(Second_user__id=self.scope['user'].id)&Q(First_user__id=to_user.id)&Q(adv__id=data['adv_id'])))
            except Chat.DoesNotExist:
                this_chat=Chat(First_user=self.scope['user'],Second_user=to_user,adv=data['adv'])
                os.makedirs(str(MEDIA_ROOT/'chat'/str(this_chat.id)))
                await this_chat.asave()
                await self.channel_layer.group_send(f"user-{self.scope['user'].id}",{"type":"chat.created","from_user":{'id':self.scope['user'].id,'username':self.scope['user'].username},"to_user":{'id':to_user.id,'username':to_user.username}})
                await self.channel_layer.group_send(f"user-{to_user.id}",{"type":"chat.created","from_user":{'id':to_user.id,'username':to_user.username},"to_user":{'id':self.scope['user'].id,'username':self.scope['user'].username}})
                await self.send_json({"type":"status","status":"CHAT_CREATED"})
            to_user = await self.get_second_user(this_chat,from_user)
            if data['type']=='image':
                #  img = Image(message['file'])
                #  img.save(this_chat.media/f"{str(datetime.datetime.now())}.jpg")
                 message = f"{this_chat.media_for_web}/{str(datetime.datetime.now())}.jpg"
            elif data['type']=='video':
                #  with open(str(this_chat.media/f"{message['name'].split('.')[0]}{str(datetime.datetime.now)}.{message['name'].split('.')[1]}"),'wb') as f:
                    #   f.write(message['file'])
                    #   f.close()
                      message = f"{this_chat.media_for_web}/{message['name'].split('.')[0]}{str(datetime.datetime.now)}.{message['name'].split('.')[1]}"
            msg = Message(type=data["type"],text=message,timestamp=datetime.datetime.now(),user=from_user,read=False)
            await msg.asave()
            await this_chat.Messages.aadd(msg)
            await self.channel_layer.group_send(f"user-{to_user.id}",
            {"type": "chat.message",
            'user':await sync_to_async(from_user.get_username)(),
            "you":False,
            "user-id":from_user.id,
            'message_type':data['type'],
            "text":message,
            "adv_id":data['adv_id']}
            )
            if not users_online.get(to_user,None):
                 payload = {"head":f"Пришло сообщение от {await sync_to_async(from_user.get_username)()}","body":message if data['type']=='text' else '(медиафайл)',"url":reverse("chat")}
                 try:
                    await sync_to_async(send_user_notification)(to_user,payload=payload,ttl=1200)
                 except:
                      pass
                 notific = Notification(Head=payload["head"],Body=payload["body"],Read=False,Timestamp = datetime.datetime.now(),Url=reverse("chat"))
                 await notific.asave()
                 await to_user.notifications.aadd(notific) 
                 await to_user.asave()
            await self.channel_layer.group_send(f"user-{self.scope['user'].id}",
                                                {"type": "chat.message",
                                                 "you":True,
                                                 "user-id":to_user.id,
                                                 'user':await sync_to_async(from_user.get_username)(),
                                                 "text":message,
                                                 "adv_id":data['adv_id']
                                                 })
    async def chat_message(self, event):
         await self.send_json(
        {
         "type":"message",
            "you":event["you"],
            "user-id":event["user-id"],
            "username": event['user'],
            "message": event["text"],
            "adv_id":event["adv_id"]})
    async def chat_created(self,event):
         await self.send_json(
              {
                   "type":"chat.created",
                   "from_user":event["from_user"],
                   "to_user":event["to_user"]
              }
         )


