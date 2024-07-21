from asgiref.sync import sync_to_async
from users.models import Adverstiment,MyUser
from django.db.models import Avg
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
from .models import Chat

@sync_to_async
def set_session_data(key,value,request)->None:
     request.session[key]=value
@sync_to_async
def get_session_data(key,request)->str:
     return request.session[key]
@sync_to_async
def get_user_from_token(token):
     return token.user
@sync_to_async
def get_adv_id(obj): #Эта функция для того, чтобы совладать с SynchronousOnlyError
     return obj.adv.id
@sync_to_async
def get_all_chats(user):
         id = user.id
         chats = [chat for chat in Chat.objects.filter(Q(First_user=id)|Q(Second_user=id))]
         id = [chat.id for chat in chats]
         return chats,id
@sync_to_async
def get_messages(this_chat,count):
        return this_chat.Messages.order_by("-timestamp")[count*20:20*(count+1)]
@sync_to_async
def get_msg_info(msg):
    msg = {"id":msg.id,"type":msg.type,"text":msg.text,"user":msg.user,"timestamp":msg.timestamp.strftime('%m/%d/%Y, %H:%M:%S'),"read":msg.read}
    return msg
@sync_to_async
def get_second_user(this_chat,from_user):
        to_user = this_chat.Second_user if from_user==this_chat.First_user else this_chat.First_user 
        return to_user
@sync_to_async
def get_count_of_unreaded_messages(user,to_user):
        chat = Chat.objects.filter((Q(First_user=user)&Q(Second_user=to_user))|(Q(Second_user=user)&Q(First_user=to_user)))
        messages = [i.Messages.filter(user=to_user,read=False).count for i in chat]
        return messages
@sync_to_async
def get_user(request)->MyUser:
    return request.user if bool(request.user) else None
@sync_to_async
def get_count_all(model)->int:
    return model.all().count()
@sync_to_async
def get_second_users(chats,user)->list:
    return [{"user":chat.First_user if user==chat.Second_user else chat.Second_user,"adv":chat.adv} for chat in chats]
@sync_to_async
def get_rating(user)->float:
    return user.reviews.aggregate(Avg('rating'))['rating__avg']
@sync_to_async
def contains_in(what,query_set)->True|False:
    return what in query_set.all()
async def search_advs(search:str,category:str,count:int,user)->list:
    if search == "":
            if category!="":
                    if (not user.is_authenticated):
                        advs = [adv async for adv in Adverstiment.objects.filter(category=category).order_by("datetime")[count*20:20*(count+1)]]
                    else:
                        ban_list = [user.id async for user in user.ban_list.all()]
                        recs = user.recommendations[category][count*20:20*(count+1)]
                        advs = [adv async for adv in Adverstiment.objects.filter(id__in=recs,category=category).exclude(sold_by_user_id__in=ban_list)]
                        d = dict([adv.id,adv] for adv in advs)
                        advs = []
                        for i in recs:
                             if i in d:advs.append(d[i])
                        if len(advs)==0:
                            advs = [adv async for adv in Adverstiment.objects.filter(category=category).order_by("datetime")[count*20:20*(count+1)]]

            else:
                if  (not user.is_authenticated):
                    advs =[adv async for adv in Adverstiment.objects.all().order_by("datetime")[count*20:20*(count+1)]]
                else:
                    ban_list = [user.id async for user in user.ban_list.all()]
                    count_history = await get_count_all(user.history)
                    if (count_history==0):
                        advs =[adv async for adv in Adverstiment.objects.exclude(sold_by_user_id__in=ban_list).order_by("datetime")[count*20:20*(count+1)]]
                    else:
                        try:
                            recs = user.recommendations["all"][count*20:20*(count+1)]
                            advs = [adv async for adv in Adverstiment.objects.filter(id__in=recs).exclude(sold_by_user_id__in=ban_list)]
                            d = dict([adv.id,adv] for adv in advs)
                            advs = []
                            for i in recs:
                                if i in d:advs.append(d[i])
                            if len(advs)==0:
                                     advs =[adv async for adv in Adverstiment.objects.exclude(sold_by_user_id__in=ban_list).order_by("datetime")[count*20:20*(count+1)]]
                        except TypeError as e:
                            advs =[adv async for adv in Adverstiment.objects.exclude(sold_by_user_id__in=ban_list).order_by("datetime")[count*20:20*(count+1)]]


    else:
            ban_list = []
            if user.is_authenticated:
                 ban_list = [user async for user in user.ban_list.all()]
            if category=="":
                advs = [adv async for adv in Adverstiment.objects.annotate(similarity=TrigramSimilarity('main_name', search),).filter(Q(main_name__unaccent__icontains=search)|Q(similarity__gt=0.1)).exclude(sold_by_user_id__in=ban_list).order_by('-similarity',"datetime")[count*20:20*(count+1)]]
            else:
                advs = [adv async for adv in Adverstiment.objects.annotate(similarity=TrigramSimilarity('main_name', search),).filter(Q(main_name__unaccent__icontains=search,category=category)|Q(similarity__gt=0.1,category=category)).exclude(sold_by_user_id__in=ban_list).order_by('-similarity',"datetime")[count*20:20*(count+1)]]
    return advs