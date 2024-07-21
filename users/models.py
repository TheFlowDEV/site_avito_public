from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import json
import os
from django.dispatch import receiver
from authlib.integrations.django_client import token_update
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import pre_delete
from asgiref.sync import sync_to_async
def empty_recs():
    return  {'all':[],
              'Одежда':[],
              'Канцелярия':[],
              'Товары для дома':[],
              'Электроника':[],
              'Хобби и творчество':[],
                'Украшения и бижутерия':[],
                'Здоровье':[],
                'Бытовая техника':[],
                'Разное':[]
                }
              
              
class Adverstiment(models.Model):
    cost = models.IntegerField(validators=[
            MaxValueValidator(1000000),
            MinValueValidator(1)
        ])
    text = models.TextField()
    main_name = models.TextField()
    category = models.TextField()
    is_active = models.BooleanField()
    datetime = models.DateTimeField()
    sold_by_user_id = models.IntegerField()
    order_image_list=models.JSONField(default=list)
    @property
    def media(self)->os.PathLike:
        return settings.BASE_DIR/"media"/"images"/str(self.sold_by_user_id)/str(self.id)
    def media_for_web(self):
        return "media"+'/'+"images"+'/'+str(self.sold_by_user_id)+'/'+str(self.id)
    def get_photoname(self)->list:
            l = []
            try:
                if len(self.order_image_list)==0 or len(os.listdir(self.media))!=len(self.order_image_list)-1:
                    self.order_image_list = [i for i in os.listdir(self.media)]
            except:
                self.order_image_list = [i for i in os.listdir(self.media)]
            for i in self.order_image_list:
                    l.append(i.split('.')[0])
            return  l
    def get_photo_redact(self,one:bool):
        if one:
            try:
                if len(os.listdir(self.media)):
                    for i in os.listdir(self.media):
                        if "primary" in i:
                            return self.media_for_web()+"/"+i
                    return None
                else:
                    return None  
            except:

                    return None
        else:
            l = []
            l2 = []
            try:
                if len(self.order_image_list)==0 or len(os.listdir(self.media))!=len(self.order_image_list)-1:
                    self.order_image_list = [i for i in os.listdir(self.media)]
            except:
                self.order_image_list = [i for i in os.listdir(self.media)]
            for i in self.order_image_list:
                if "primary" not in i:
                    l.append(self.media_for_web()+"/"+str(i))
                    l2.append(str(i))
            
            return  zip(l,l2)
    def get_photo(self,one:bool)->list|str:
        if one:
            try:
                if len(os.listdir(self.media)):
                    for i in os.listdir(self.media):
                        if "primary" in str(i).split('.')[0]:
                            return self.media_for_web()+"/"+i
                    return self.media_for_web()+"/"+os.listdir(self.media)[0]
                else:
                    return "static"+'\\'+"unknown.png"  
            except:
                    return "static"+'\\'+"unknown.png" 
        else:
            l = []
            try:
                if len(self.order_image_list)==0 or len(os.listdir(self.media))!=len(self.order_image_list)-1:
                    self.order_image_list = [i for i in os.listdir(self.media)]
            except:
                self.order_image_list = [i for i in os.listdir(self.media)]
            for i in self.order_image_list:
                if "primary" not in str(i).split('.')[0]:
                    l.append(self.media_for_web()+"/"+str(i))
            return  l
class Review(models.Model):
    rating = models.IntegerField(default=0)
    text = models.TextField(default="")
    adverstiment = models.ForeignKey("Adverstiment",on_delete=models.CASCADE)
    wrote_by = models.TextField(default='1')
class Notification(models.Model):
    Head= models.TextField()
    Body = models.TextField()
    Read = models.BooleanField(default=False)
    Timestamp = models.DateTimeField()
    Url = models.URLField()
class MyUser(AbstractUser):
    email=models.EmailField(unique=True)
    username=models.TextField(unique=True)
    university = models.TextField()
    reviews = models.ManyToManyField(Review,blank=True)
    user_adverstiments= models.ManyToManyField(Adverstiment,blank=True,related_name="user_advs")
    user_buys = models.ManyToManyField(Adverstiment,blank=True,related_name="user_buys")
    phone_number = models.TextField(null=True,blank=True)
    related_adverstiments = models.ManyToManyField(Adverstiment,blank=True,related_name="related_adverstiments")
    history = models.ManyToManyField(Adverstiment,blank=True,related_name="click_history") #история для формирования рекомендаций
    recommendations = models.JSONField(default=empty_recs)
    notifications = models.ManyToManyField(Notification,blank=True)
    subscriptions = models.ManyToManyField('MyUser',blank=True,related_name='subscriptions_set')
    ban_list = models.ManyToManyField('MyUser',blank=True,related_name='ban_set')
    @property
    def media(self)->os.PathLike:
        if not os.path.exists(str(settings.BASE_DIR/"media"/"images"/str(self.id))):
            os.makedirs(str(settings.BASE_DIR/"media"/"images"/str(self.id)))
        return settings.BASE_DIR/"media"/"images"/str(self.id)
    @property
    def media_for_web(self):
        return "media"+'/'+"images"+'/'+str(self.id)
    @property
    def photo(self):
            for i in os.listdir(self.media):
                if "primary" in str(i).split('.')[0]:
                    return self.media_for_web+"/"+str(i)
            return settings.STATIC_URL+'unknown_user.png'
class OAuth2Token(models.Model):
    name = models.TextField()
    access_token = models.TextField()
    token_type = models.TextField(null=True)
    refresh_token = models.TextField(null=True)
    expires_at = models.PositiveIntegerField(null=True)
    user = models.ForeignKey(MyUser,on_delete=models.CASCADE)
    oauth_id = models.TextField() #Идентификация по возвращемому id с OAUTH сервера
    def to_token(self):
        return dict(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            token_type=self.token_type,
            expires_at=self.expires_at,
        )

def delete_adverstiment_from_recs(sender, instance, using,**kwargs):
    id = instance.id
    user = instance.user_advs.get()
    recs = user.get_recommendations()
    for key,value in recs.items():
        recs[key]=value.remove(id)
    user.set_recommendations(recs)
    user.save()
pre_delete.connect(delete_adverstiment_from_recs,sender=Adverstiment)

@receiver(token_update)
def on_token_update(sender, name, token, refresh_token=None, access_token=None, **kwargs):
    if refresh_token:
        item = OAuth2Token.objects.get(name=name, refresh_token=refresh_token)
    elif access_token:
        item = OAuth2Token.objects.get(name=name, access_token=access_token)
    else:
        return

    # update old token
    item.access_token = token['access_token']
    item.refresh_token = token.get('refresh_token')
    item.expires_at = token['expires_at']
    item.save()