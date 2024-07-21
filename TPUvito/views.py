from django.contrib.auth import get_user_model
from users.models import Adverstiment
from .models import Chat
from django.apps import apps
from django.contrib.auth import login
from django.db.models import Q
from django.shortcuts import render
import aiohttp
import json
from django.http import HttpResponse
from django.urls import reverse
from asgiref.sync import sync_to_async
from django.contrib.auth import authenticate
from .async_func import *
from rest_framework_simplejwt.tokens import RefreshToken
from .settings import oauth,secret_key_vk
from django.shortcuts import redirect
from authlib.common.urls import add_params_to_uri
import uuid
User = get_user_model()
OAuth2Token = apps.get_model('users.OAuth2Token')

async def index(request):
    search = request.GET.get("text","")
    count =  int(request.GET.get("count",0))
    category = request.GET.get("category","")
    user = await get_user(request)
    advs = await search_advs(search,category,count,user)
    history=[]
    rel_advs=[]
    if category: more_than_20=await sync_to_async(Adverstiment.objects.filter(category=category).count)()
    else: more_than_20 = await sync_to_async(Adverstiment.objects.all().count)()
    more_than_20=True if more_than_20>20 else False
    mobile = request.user_agent.is_mobile
    print(mobile,request.user_agent)
    if user.is_authenticated:
        notif_count =len([notif async for notif in user.notifications.filter(Read=False)])
        notif_count = notif_count if notif_count!=0 else ''
        if category=="":history = [adv async for adv in user.history.all()[:6]]
        else: history = [adv async for adv in user.history.filter(category=category)[:6]]
        if len(history)==0:history = []
        rel_advs = [adv async for adv in user.related_adverstiments.all()]
    else:notif_count = ''
    return render(request,template_name="index.html",context={"advs":advs,"notif_count":notif_count,"history":history,"rel_advs":rel_advs,"more_than_20":more_than_20,"mobile":mobile})

async def adverstiment(request):
    request_user =await get_user(request)
    adv_id = request.GET.get("adv_id",None)
    try:
        user_adv = await User.objects.aget(user_adverstiments=adv_id)
    except:
        return HttpResponse("Error.Not found!")
    adv = await Adverstiment.objects.aget(id=adv_id)
    author = False
    is_favorite = None
    
    try:
        adv = await request_user.related_adverstiments.aget(id=adv_id)
        is_favorite=True
    except:
        is_favorite=False
    if (not adv_id) and (not user_adv) and (not adv):
        return HttpResponse("404 Error. Not found!")
    if request_user == user_adv:
        author = True
    notif_count=''
    if request_user.is_authenticated:
        notif_count =len([notif async for notif in request_user.notifications.filter(Read=False)])
        notif_count = notif_count if notif_count!=0 else ''
    return render(request,template_name="adverstiments.html",context={"notif_count":notif_count,
                                                                      'rating':await get_rating(user_adv),
                                                                      'user_adv':user_adv,
                                                                      'adv':adv,
                                                                      'author':author,
                                                                      'is_favorite':is_favorite,
                                                                      'is_active':adv.is_active})

async def chat(request,user_id="",adv_id=""):
    user = await get_user(request)
    if user.is_authenticated:
        context={}
        if user_id!="" and adv_id!="" and user_id!=str(user.id):
            context["new_user"]={"user":await User.objects.aget(id=user_id),"adv":await Adverstiment.objects.aget(id=adv_id)}
            contains =await contains_in(context["new_user"]["adv"],context["new_user"]["user"].user_adverstiments)
            if not contains:
                return HttpResponse("Ошибка")
        chats = await sync_to_async(Chat.objects.filter)(Q(First_user=user)|Q(Second_user=user))
        second_users = await get_second_users(chats,user)
        context["users"]=second_users
        rating = await get_rating(user)
        my_profile = True
        context["rating"]=rating
        context["my_profile"]=my_profile
        return render(request,"chat.html",context=context)
    else:
        return HttpResponse("Войдите пожалуйста или зарегистрируйтесь.")

async def profile(request):
    request_user = await get_user(request)
    id = request.GET.get("id",request_user.id)
    if not id:
        return HttpResponse("Пожалуйста, зарегистрируйтесь, чтобы получить доступ к профилю")
    user = await User.objects.aget(id=id)
    rating = await get_rating(user)
    use_favorite = request.GET.get("use_favorite",False)
    notif_count=''
    if not user:
        return HttpResponse("Не найдено. Ошибка 404. Пожалуйста вернитесь на главную страницу")
    rel_advs=[]
    if request_user.is_authenticated:
        notif_count =len([notif async for notif in request_user.notifications.filter(Read=False)])
        notif_count = notif_count if notif_count!=0 else ''
    my_profile = False
    blocked = None
    if request_user==user:
        my_profile = True #принадлежность профиля
        subscribed= None
        if use_favorite:
            advs = [adv async for adv in request_user.related_adverstiments.all()[0:20]]
        else:
            advs = [adv async for adv in request_user.user_adverstiments.filter(is_active=True)[0:20]]
    else:
        if request_user.is_authenticated:
            subscribed = await contains_in(user,request_user.subscriptions.all())
            rel_advs=[adv async for adv in request_user.related_adverstiments.filter(sold_by_user_id=user.id,is_active=True)[0:20]]
            blocked =await contains_in(user,request_user.ban_list)

        else:
            subscribed=None
            rel_advs=[]
        advs = [adv async for adv in user.user_adverstiments.filter(is_active=True)[0:20]]
    return render(request,"profile.html",context={'user_adv':user,
                                                  "rating":rating,
                                                  'notif_count':notif_count,
                                                  'my_profile':my_profile,
                                                  'use_favorite':use_favorite,
                                                  "advs":advs,
                                                  'rel_advs':rel_advs,
                                                  'reviews_count':await get_count_all(user.reviews),
                                                  'subscribers_count':await get_count_all(user.subscriptions_set.all()),
                                                  'subscribes_count':await get_count_all(user.subscriptions.all()),
                                                  'subscribed':subscribed,
                                                  'blocked':blocked
                                                  })

async def add_adv(request):
    request_user = await get_user(request)
    id = request.GET.get("id",request_user.id)
    if not id:
        return HttpResponse('User is not authenticated')
    notif_count =len([notif async for notif in request_user.notifications.filter(Read=False)])
    notif_count = notif_count if notif_count!=0 else ''
    return render(request,"add_adv.html",context={'notif_count':notif_count})

async def login_TPU(request):
    redirect_uri = await sync_to_async(request.build_absolute_uri)('/authorize_tpu')
    return await sync_to_async(oauth.TPU.authorize_redirect)(request,redirect_uri)
async def authenticate_TPU(request):
        token = oauth.TPU.authorize_access_token(request)
        resp = oauth.TPU.get(add_params_to_uri('https://api.tpu.ru/v2/auth/user',[('apiKey','02acac4c18e268ff8e06b79acef9027d')]), token=token)
        resp.raise_for_status()
        profile = resp.json()

        set_session_data('user_data',{'id':profile['user_id'],'email':profile['email']},request)
        set_session_data('token',{'name':'TPU','access_token':token['access_token'],'refresh_token':token['refresh_token']},request)
        request.session.modified = True
        user = None
        django_token = None
        try:
            django_token = await OAuth2Token.objects.aget(oauth_id=profile['user_id'])
            user = await get_user_from_token(django_token)
            django_token.access_token = token['access_token']
            django_token.refresh_token = token['refresh_token']
            django_token.expires_at=3600
            await django_token.asave(update_fields=['access_token','refresh_token','expires_at'])
        except OAuth2Token.DoesNotExist:
            try:
                user = await User.objects.aget(email=profile['email'])
            except User.DoesNotExist:
                return redirect(reverse('bind_oauth'))
            django_token = await OAuth2Token.objects.aupdate_or_create(name='TPU',access_token=token['access_token'],token_type='Bearer',refresh_token=token['refresh_token'],expires_at=3600,user=user,auth_id=profile['user_id'])
            await django_token.asave()
        await sync_to_async(login)(request,user)
        return redirect(reverse('index'))

async def authenticate_vk(request):
        data = json.loads(request.GET.get('payload'))
        if data.get('type')=="silent_token":

            silent_token = data.get('token')
            token = None
            user_id = None
            email=None
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.vk.com/method/auth.exchangeSilentAuthToken',params={'token':silent_token,'v':'5.131','access_token':secret_key_vk,'uuid':data.get('uuid')}) as response:
                    json_data =await response.json()
                    if json_data.get('error')!=None:
                        return HttpResponse('Ошибка, вернись назад')
                    token = json_data['response'].get('access_token')
                    user_id = json_data['response'].get('user_id')
                    email = json_data['response'].get('email')
            await set_session_data('user_data',{'id':user_id,'email':email},request)
            await set_session_data('token',{'name':'VK','access_token':token},request)
            user = None
            django_token = None
            try:
                django_token = await OAuth2Token.objects.aget(oauth_id=user_id)
                user = await get_user_from_token(django_token)
                django_token.access_token = token
                await django_token.asave(update_fields=['access_token'])
            except OAuth2Token.DoesNotExist:
                try:
                    user = await User.objects.aget(email=email)
                except User.DoesNotExist:
                    return redirect(reverse('bind_oauth'))
                django_token = await OAuth2Token.objects.aupdate_or_create(name='VK',access_token=token,user=user,auth_id=user_id)
                await django_token.asave()
            await sync_to_async(login)(request,user)
            return redirect(reverse('index'))
async def bind_oauth(request):
    # if request.session['token']:
        if request.method=='GET':
            return render(request,'register_oauth.html')
        else:
            data = request.POST
            bind_type = data.get('bind_type',None)
            if not bind_type:
                return HttpResponse('ERROR!')
            if bind_type=='register':
                email = data.get('email',None)
                username = data.get('username',None)
                name = await get_session_data('token',request)
                name = name['name']
                token_data = await get_session_data('token',request)
                user_data=await get_session_data('user_data',request)

                if not email:
                    email =user_data['email']
                if not username:
                    username = f'пользователь-{uuid.uuid5(uuid.NAMESPACE_DNS,email)}'
                user = User(email=email,username=username)
                if not data.get('password'):
                    return HttpResponse('ERROR!')
                user.set_password(data['password'])
                await user.asave()
                if name=="VK":
                        token,created = await OAuth2Token.objects.aupdate_or_create(name=name,access_token= token_data['access_token'],user=user,oauth_id=user_data['id'])
                else:
                        token,created = await OAuth2Token.objects.aupdate_or_create(name=name,access_token= token_data['access_token'],token_type='Bearer',refresh_token=token_data['refresh_token'],user=user,oauth_id=user_data['id'])
                await token.asave()
                await sync_to_async(login)(request,user)
                return redirect('index')
            elif bind_type=='login':
                email = data.get('email',None)
                if not email:
                    return HttpResponse('Ошибка! Электронная почта не определена')
                password = data.get('password',None)
                if not password:
                    return HttpResponse('Ошибка! Пароль не определён')
                user = await sync_to_async(authenticate)(request=request,email=email,password=password)
                if user:
                    # try:
                        name = await get_session_data('token',request)
                        name = name['name']
                        token_data = await get_session_data('token',request)
                        user_data=await get_session_data('user_data',request)
                        if name == 'VK':
                            token,created = await OAuth2Token.objects.aupdate_or_create(name=name,access_token= token_data['access_token'],user=user,oauth_id=user_data['id'])
                        else:
                            token,created = await OAuth2Token.objects.aupdate_or_create(name=name,access_token= token_data['access_token'],token_type='Bearer',refresh_token=token_data['refresh_token'],user=user,oauth_id=user_data['id'])
                        await token.asave()
                        await sync_to_async(login)(request=request,user=user)
                        return redirect('index')
                    # except Exception as e:
                    #     return HttpResponse('Подозрительная ошибка с токеном!' +str(e))
                else:
                    return HttpResponse('USERNOTFOUND ERROR!')
    # else: 
    #     return HttpResponse('Ошибка, вернитесь назад')