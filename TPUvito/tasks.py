from .recommendations.recommendations import update_recommendations,update_recommendations_category
from asgiref.sync import sync_to_async
from webpush import send_user_notification
from django.urls import reverse
from django.apps import apps
from django.utils import timezone
from django.contrib.auth import get_user_model
import dramatiq
User = get_user_model()
Notification = apps.get_model("users","Notification")

@dramatiq.actor
async def recommendations_to_DB(users,category=None):
                if type(users)!=list:
                        users=[users]
                for user_json in users:
                    id_history = user_json["history"]
                    if len(id_history)!=0:
                        raw_recs = await update_recommendations(id_history)
                        res = []
                        user = await User.objects.aget(id=user_json["id"])
                        for i in raw_recs.id :
                                res.append(i)
                        dict_rec = user.recommendations
                        dict_rec["all"]=res
                        if category:
                            cat_id_history = [adv.id async for adv in user.history.filter(category=category)]
                            if len(cat_id_history)!=0:
                                raw_cat_recs = await update_recommendations_category(cat_id_history,category)
                                res = []
                                for i in raw_cat_recs.id :
                                        res.append(i)
                                dict_rec[category]=res
                        user.recommendations=dict_rec
                        payload = {"head":"Мы нашли для вас кое-что новенькое!","body":"Хотите посмотреть?","url": reverse("index")}
                        try:
                                await sync_to_async(send_user_notification)(user,payload)
                        except:
                              print('user is not connected to notify') 
                        notific = Notification(Head=payload["head"],Body=payload["body"],Read=False,Timestamp = timezone.now(),Url=reverse("index"))
                        await notific.asave()
                        await sync_to_async(user.notifications.add)(notific) 
                        await user.asave()
