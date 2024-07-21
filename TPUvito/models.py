from django.db import models
from django.contrib.auth import get_user_model
from encrypted_model_fields.fields import EncryptedTextField
from .settings import MEDIA_ROOT

User = get_user_model()
class Message(models.Model):
    type = models.TextField()
    text= EncryptedTextField()
    timestamp = models.DateTimeField()
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    read = models.BooleanField()
class Chat(models.Model):
    First_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="first_user")
    Second_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="second_user")
    adv = models.ForeignKey("users.Adverstiment",on_delete=models.CASCADE)
    Messages =  models.ManyToManyField(Message)
    @property
    def media(self):
        return MEDIA_ROOT/'chat'/str(self.id)
    @property
    def media_for_web(self):
        return f'/media/chat/{self.id}'
class Report(models.Model):
    Head = models.TextField()
    Description = models.TextField()
    Timestamp = models.DateTimeField()
    From_user = models.ForeignKey(User,on_delete=models.CASCADE)

