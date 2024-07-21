
from django.contrib.auth import get_user_model,authenticate,login,logout
from users.models import Adverstiment,Review
from .models import Chat,Report
from django.db.models import Q
from adrf.views import APIView
import random
from webpush import send_user_notification
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from asgiref.sync import sync_to_async
import os
from django.utils.html import strip_tags
from .serializers import *
from django.urls import reverse
import datetime
from django.utils import timezone
from PIL import Image, ImageOps, ImageDraw
from rest_framework_simplejwt.tokens import RefreshToken
from .settings import BASE_DIR,PRODUCT_CATEGORIES,MEDIA_ROOT
from django.apps import apps
from .tasks import recommendations_to_DB
User = get_user_model()
from .async_func import *
Notification = apps.get_model("users","Notification")
Review = apps.get_model('users','Review')
class ChangePassword(APIView):
    async def post(request):
        data = request.data
        user = await get_user(request)
        if user.check_password(data['old_password']):
            user.set_password(data['new_password'])
            return Response({'status':'OK'})
        else:
            return Response({'status':'ERROR'})
class Ban(APIView):
    permission_classes=[IsAuthenticated]
    async def post(self,request):
        data = request.data
        user = await get_user(request)
        ban_type = data['type'] 
        to_user=None
        try: 
            to_user = await User.objects.aget(username=data['to_user'])
        except User.DoesNotExist:
            return Response({'status':'ERROR','description':'USER NOT FOUND'})
        if ban_type =='ban':
            await user.ban_list.aadd(to_user)
        elif ban_type=='unban':
            await user.ban_list.aremove(to_user)

        return Response({'status':'Success!','description':'OK'})
class Subscribe(APIView):
    permission_classes=[IsAuthenticated]
    async def post(self,request):
        data = request.data
        subscribe = data.get('subscribe',None)
        user = await get_user(request)
        if not data.get('to_user',None) and not subscribe:
            return Response({'status':'FAILED'})
        to_user = await User.objects.aget(username=data['to_user'])
        if user == to_user:
            return Response({'status':'FAILED'})
        if subscribe:
            await user.subscriptions.aadd(to_user)
        else:
            await user.subscriptions.aremove(to_user)
        return Response({'status':'Success'})
class ChangeUserData(APIView):
    permisson_classes=[IsAuthenticated]
    async def post(self,request):
        user = await get_user(request)
        data = request.data
        user.username = strip_tags(data.get('username',user.username))
        user.email = strip_tags(data.get('email',user.email))
        user.phone_number = strip_tags(data.get('phone')) if data.get("phone") else user.phone_number
        photo = request.FILES.get('photo',None)
        if photo:
            img = Image.open(photo)
            img = img.convert('RGB')
            size = (76, 76)
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask) 
            draw.ellipse((0, 0) + size, fill=255)
            output = ImageOps.fit(img,mask.size,centering=(0.5,0.5))
            output.putalpha(mask)
            output.save(str(user.media/'primary.png'))
        await user.asave(update_fields=['username','email','phone_number'])
        return Response({'status':'Success'})
        

class NotificationGetter(APIView):
    permission_classes=[IsAuthenticated]
    async def get(self,request):
        user =await get_user(request)
        count = request.GET.get('count',0)
        notifications = [notif async for notif in user.notifications.filter(Read=False)[count*20:(count+1)*20]]
        message={"status":"OK",'notifications':await NotificationSerializer(notifications,many=True).adata}
        for i in notifications:
            i.Read=True
            await i.asave(update_fields=["Read"])
        return Response(message)
    async def post(self,request):
        user = await get_user(request)
        read_id = request.data.get('read_id',None)
        if read_id:
            notif  = await user.notifications.aget(id = read_id)
            notif.Read= True
            await notif.asave(update_fields=["Read"])
            return Response({'status':'Success'})
        else:
            return Response({'status':'ERROR'})
class ReportHandler(APIView):
    permission_classes=[IsAuthenticated]
    async def post(self,request):
        head = request.data["head"]
        user = await get_user(request)
        description = request.data["description"]
        rep = Report(Head=head,Description=description,Timestamp=timezone.now(),From_user=user)
        await rep.asave()
        return Response({"status":"OK"})
class UpdateAdverstiment(APIView):
    parser_classes=[MultiPartParser]
    permission_classes=[IsAuthenticated]
    async def post(self,request):
        print(request.data)
        id = request.data["id"]
        data = request.data
        
        adverstiment = await Adverstiment.objects.aget(id=id)
        
        if adverstiment.sold_by_user_id!=request.user.id:
            return Response({"status":"ERROR"})
        if not adverstiment.is_active:
            return Response({"status":"ERROR",'description':"non-active adverstiment"})
        if data.get("category",adverstiment.category) not in PRODUCT_CATEGORIES:
            return Response({'status':'ERROR'})
        adverstiment.text = data.get("text",adverstiment.text) if data.get("text",adverstiment.text) != "" else adverstiment.text
        adverstiment.cost = int(data.get("price",adverstiment.cost)) if data.get("price",adverstiment.cost) != "" else int(adverstiment.cost)
        adverstiment.main_name = data.get("main_name",adverstiment.main_name) if data.get("main_name",adverstiment.main_name) != "" else adverstiment.main_name
        adverstiment.is_active = True if data.get("is_active",adverstiment.is_active)=="true" or  data.get("is_active",adverstiment.is_active)==True else False
        await adverstiment.asave(update_fields=["category","text","cost","main_name","is_active"])
        change_photos = data.get("change_photo",None) 
        if change_photos=="ADD":
            photos = request.FILES.getlist("file",None)#photo:{name:'name.jpg',file:file_descriptor}
            if not photos:
                return Response({"status":'ERROR,PHOTOS ARE NOT FOUND!'})
            photos=[{"name":i.name,"data":i.file} for i in photos]
            path = adverstiment.media
            if len(os.listdir(path))>0:
                if os.listdir(path)[-1].split('_')[0].isdigit():
                    last_index = int(os.listdir(path)[-1].split('.')[0])+1
                else:
                    last_index=0
            else:
                last_index='primary'
            for i in photos:
                img = Image.open(i['data'])
                img = img.convert('RGB')
                new_name = f"{last_index}_{datetime.datetime.now().strftime('%d-%m-%Y__%H-%M-%S')}_{random.randint(0,100)}.jpg"
                img.save(f"{path}/{new_name}")
                if last_index=="primary":
                    last_index=1
                    if adverstiment.order_image_list!=[]:
                        adverstiment.order_image_list[0]=new_name
                    else:
                        adverstiment.order_image_list=[new_name]
                else:
                        adverstiment.order_image_list=(adverstiment.order_image_list+[new_name])
                        last_index+=1
                print(adverstiment.order_image_list)
                await adverstiment.asave(update_fields=["order_image_list"])
        elif change_photos =="DELETE":
            path = adverstiment.media
            if len(os.listdir(path)):
                photos = data.getlist("photos",None)#photos:[1,2,3,4,5,6]
                print(photos)
                if type(photos)==str:photos = [photos]
                if not photos: return Response({"status":'ERROR','description':'PHOTOS ARE NOT FOUND!'})
                photos = [i.replace("old_","") for i in photos]
                new_primary = False
                for i in photos:
                    try:
                        if "primary" in i:
                            os.remove(f"{path}/{i}")
                            new_primary = True
                        else:os.remove(f"{path}/{i}")
                    except:
                        print("Не удалось удалить файл ",i)
                adverstiment.order_image_list=[str(i) for i in adverstiment.order_image_list if i not in photos]
                if new_primary:
                    if len(os.listdir(path)):
                        os.rename(f"{path}/{adverstiment.order_image_list[0]}",f"{path}/primary_{datetime.datetime.now().strftime('%d-%m-%Y__%H-%M-%S')}_{random.randint(0,1000)}.jpg")
                        adverstiment.order_image_list=adverstiment.order_image_list[1:]
                await adverstiment.asave(update_fields=["order_image_list"])
        elif change_photos =="SET_PRIMARY":
            primary_photo = data.get("primary_photo",None)
            if not primary_photo: return Response('ERROR,PHOTOS ARE NOT FOUND!')
            path = adverstiment.media
            img = Image.open(primary_photo.file)
            for i in os.listdir(path):
                if "primary" in str(i).split('.')[0]:
                    old_img = Image.open(path+"/"+i)
                    old_img.save(os.path.join(path,f"{len(os.listdir(path)-1)}_{datetime.datetime.now().strftime('%d-%m-%Y__%H-%M-%S')}_{random.randint(0,1000)}.jpg"))
                    os.remove(i)
            new_name = f"primary_{datetime.datetime.now().strftime('%d-%m-%Y__%H-%M-%S')}_{random.randint(0,1000)}.jpg"
            adverstiment.order_image_list[0]=new_name
            img.save(os.path.join(adverstiment.media,new_name))

        elif change_photos=="CHANGE_ORDER":
            if 'primary.jpg' in data['order']:
                return Response({"status":'ERROR! primary.jpg was found!'})
            adverstiment.order_list=(adverstiment.order_image_list[0]+data["order"])
            await adverstiment.asave()
        return Response({'status':'Success'})
class Chat_API(APIView):
    async def post(self,request):
        user = await get_user(request)
        if user.is_authenticated:
            request_type = request.data["type"]
            if request_type=="get_id":
                second_username=request.data["username"]
                try:
                    chat = await Chat.objects.aget((Q(First_user=user)|Q(Second_user__username=second_username))&(Q(Second_user=self.user)|Q(First_user__username=second_username)))
                except Chat.DoesNotExist:
                    return Response({"status":"ERROR","description":"CHAT NOT FOUND"})
                return Response({"status":"Success","ID":self.chat.id})
            elif request_type == 'load_file':
                this_chat = await Chat.objects.aget(id=request.data['chat_id'])
                if request.data['filetype']=='img':
                    img = Image(request.FILES.get('file'))
                    img.save(this_chat.media/f"{str(datetime.datetime.now().strftime('%d-%m-%Y__%H-%M-%S'))}.jpg")
                else:
                    with open(str(this_chat.media/f"{request.FILES.get('file')['name'].split('.')[0]}-{str(datetime.datetime.now().strftime('%d-%m-%Y__%H-%M-%S'))}.{request.FILES.get('file')['name'].split('.')[1]}"),'wb') as f:
                        f.write(request.FILES.get('file'))
                        f.close()
            elif request_type=="create_chat":
                second_user=await User.objects.aget(id=request.data["user_id"])
                adv_id=request.data["adv_id"]
                chat = None
                try:
                    chat = await Chat.objects.aget((Q(First_user=user)&Q(Second_user=second_user)&Q(adv__id=adv_id))|(Q(Second_user=user)&Q(First_user=second_user)&Q(adv__id=adv_id)))
                except Chat.DoesNotExist as e:
                    chat = Chat(First_user=user,Second_user=second_user,adv=await Adverstiment.objects.aget(id=adv_id))
                    await chat.asave()
                    os.makedirs(str(MEDIA_ROOT/'chat'/str(chat.id)))
                return Response({"status":"Success","ID":chat.id})
            elif request_type=="last_messages":
                user = await get_user(request)
                chats,chat_ids = await get_all_chats(user)
                last_message=[]
                for index,item in enumerate(chats):
                    try:
                        msg = await item.Messages.alatest('timestamp')
                    except:
                        break
                    adv_id = await get_adv_id(item)
                    msg = await get_msg_info(msg)
                    second_user = await get_second_user(item,user)
                    user = msg["user"]
                    count = await get_count_of_unreaded_messages(user,second_user)
                    first_user = {"username":user.username,"id":user.id}
                    second_user = {"username":second_user.username,"id":second_user.id}
                    ans = {
                        'type':msg["type"],'text':msg["text"],"author":{"username": first_user["username"],
                                                "id":first_user["id"]},
                                        "timestamp":msg["timestamp"],
                                        "second_user":{"username":second_user["username"],"id":second_user["id"]},"adv_id":adv_id
                                        }
                                        
                    last_message.append(ans)
                return Response({"status":'Success',"last_messages":last_message})
            elif request_type=="get_messages":
                data = request.data
                to_user = await User.objects.aget(username=data["to_user"])
                count = data.get("count",0)
                adv_id = data["adv_id"]
                this_chat = await Chat.objects.aget((Q(First_user=user)&Q(Second_user=to_user)&Q(adv__id=adv_id))|(Q(Second_user=user)&Q(First_user=to_user)&Q(adv__id=adv_id)))
                messages = await get_messages(this_chat,count)
                return Response({"status":'Success',"messages":await MessageSerializer(messages,many=True,context={'request_user':user}).adata})
            else:  
                return Response({"status":"ERROR","description":"Unknown command"})
class Login_Register(APIView):
    async def post(self,request):
        user =await get_user(request)
        if user.is_authenticated:
            data = request.data
            if data["type"]=="logout":
                    await sync_to_async(logout)(request=request)
                    if request.data.get('refresh',None):
                        RefreshToken(request.data.get('refresh',None)).blacklist()
                    if request.session.get('tpu_token',None):
                        return Response({'status':'REDIRECT','description':f"https://oauth.tpu.ru/auth/logout?redirect={reverse('index')}"})
                    return Response({"status":"Success"})
            return Response({"status":"ERROR"})
        else:
            if request.data:
                data = request.data
                if data["type"]=="register":
                    try:
                        await User.objects.aget(Q(email__iexact=data["email"])|Q(username__iexact=data["username"]))
                        return  Response({"status":'ERROR','description':"This username or email already exists"})
                    except User.DoesNotExist: 
                            user = User(email=data["email"],username=data["username"])
                            user.set_password(data["password"])
                            await user.asave()
                            await sync_to_async(login)(request,user)
                            token = await sync_to_async(RefreshToken.for_user)(user)
                            return Response({"status":"Success","jwt":{'refresh':str(token),'access':str(token.access_token)}})
                elif data["type"]=="login":
                    user = await sync_to_async(authenticate)(request=request,email=data["email"],password=data["password"])
                    if user:
                        await sync_to_async(login)(request,user)
                        token = await sync_to_async(RefreshToken.for_user)(user)
                        return Response({"status":"Success",'jwt':{'refresh':str(token),'access':str(token.access_token)}})
                    return Response({"status":"ERROR",'description':'login fail'})
                else:
                    return Response({"status":"Unknown command"})
class RevealPhone(APIView):
    async def post(self,request):
        data = request.data
        user = await get_user(request)
        to_user = await User.objects.aget(nickname=data["nickname"])
        return Response({"status":"Success","phone":to_user.phone})
class GetAdverstiments(APIView):
    async def post(self,request):
            data = request.data
            advs=[]
            if data['destination']=="main_page":
                search = data.get("text","")
                count = int(data.get("count",0))
                category = data.get("category","")
                user = await get_user(request=request)
                advs=await search_advs(search,category,count,user)
            elif data['destination']=="profile":
                type_adv =data.get('type','active')
                count = data.get('count',0)
                user = await get_user(request)
                if type_adv=="favorite":
                    advs = [adv async for adv in user.related_adverstiments.all()[count*20:(count+1)*20]]
                elif type_adv=="active":
                    id = data.get('user_id',user.id)
                    user = await MyUser.objects.aget(id=id)
                    advs = [adv async for adv in user.user_adverstiments.filter(is_active=True)[count*20:(count+1)*20]]
                elif type_adv=="inactive":
                    id = data.get('user_id',user.id)
                    user = await MyUser.objects.aget(id=id)
                    advs = [adv async for adv in user.user_adverstiments.filter(is_active=False)[count*20:(count+1)*20]]
                elif type_adv=="all":
                    #Для поиска, куда поставить отзыв
                    id = data.get('user_id',None)
                    if (id==None) or (count==None):
                        return Response({"status":"ERROR","description":"UNKNOWN COMMAND"})
                    search = data.get('text','')
                    user = await MyUser.objects.aget(id=id)
                    if search=="":
                        advs = [adv async for adv in user.user_adverstiments.all()[count*20:(count+1)*20]] 
                    else:
                        advs = [adv async for adv in user.user_adverstiments.filter(main_name__icontains=search)[count*20:(count+1)*20]]
                    print(advs,search)
                elif type_adv=="get_one_adv":
                    #Для написания отзыва
                    id = data.get('user_id',user.id)
                    to_user = await MyUser.objects.aget(id=id)
                    user = await get_user(request)
                    adv_id = data.get('adv_id',None)
                    if not adv_id:
                        return Response({"status":"ERROR","description":"UNKNOWN COMMAND"})
                    adv = await to_user.user_adverstiments.aget(id=adv_id)
                    my_review = None
                    try:
                        my_review = await to_user.reviews.aget(adverstiment=adv,wrote_by=user.id)
                    except Review.DoesNotExist as e:
                        pass
                    if my_review:
                        return Response({"status":'OK','adv':await AdverstimentSerializer(adv,context={'request_user':user,'one':True}).adata,'my_review':await ReviewSerializer(my_review).adata})
                    else:
                        return Response({"status":'OK','adv':await AdverstimentSerializer(adv,context={'request_user':user,'one':True}).adata})
            elif data['destination']=="search":
                search = data.get("text","")
                if search!="":
                    user = await get_user(request=request)
                    advs = await search_advs(search=search,category="",count=0,user=user)
                    response={"status":'OK',"advs":[{'label':adv.main_name,'value':adv.id} for adv in advs]}
                    return Response(response)
            else:
                return Response({"status":"ERROR","description":"UNKNOWN COMMAND"})
            request_user = await get_user(request)
            response ={"status":"OK","advs":await AdverstimentSerializer(advs,many=True,context={'request_user':request_user,'one':True}).adata}
            print(count)
            return Response(response)
            

class  HistoryGetter(APIView):
    permission_classes=[IsAuthenticated]
    async def post(self,request):
        data = request.data
        count = data.get("count",0)
        user = await get_user(request=request)
        ans = {"status":'OK',"history":await AdverstimentSerializer([adv async for adv in user.history.all()[count*20:(count+1)*20]],many=True,context={'request_user':user,'one':True}).adata}
        return Response(ans)
class Add_Adverstiment(APIView):
    permission_classes=[IsAuthenticated]
    async def post(self,request):
        data = request.data
        cost = data["cost"]
        main_name = strip_tags(data["main_name"])
        category = data["category"]
        if category not in PRODUCT_CATEGORIES:
            return Response({'status':'ERROR'})
        text = strip_tags(data["text"])
        user = await get_user(request)
        similar_advs = [adv async for adv in Adverstiment.objects.filter(main_name__iexact=main_name,text__iexact=text,cost__iexact=cost,category=category,sold_by_user_id=user.id)]
        photos = request.FILES.getlist("photos",None)
        if photos:
            photos=[{"name":i.name,"data":i.file} for i in photos]
        try:
            primary_photo = photos[0]
        except Exception as e:
            primary_photo={"name":"unknown.png","data":open(BASE_DIR/"static"/"unknown.png","rb")}
        if len(similar_advs)==0:
            ad = Adverstiment(cost=cost,text=text,main_name=main_name,category=category,is_active=True,sold_by_user_id=user.id,datetime=timezone.now())
            await ad.asave()
            os.makedirs(ad.media)
            primary_img = Image.open(primary_photo["data"])
            primary_img = primary_img.convert("RGB")
            new_name = f"primary_{datetime.datetime.now().strftime('%d-%m-%Y__%H-%M-%S')}_{random.randint(0,100)}.jpg"
            primary_img.save(os.path.join(ad.media,new_name))
            order_image_list  =[]
            if len(photos[1:]):
                for index,i in enumerate(photos[1:]):
                    img = Image.open(i["data"])
                    img = img.convert("RGB")
                    new_name = f"{str(index)}_{datetime.datetime.now().strftime('%d-%m-%Y__%H-%M-%S')}_{random.randint(0,100)}.jpg"
                    img.save(os.path.join(ad.media,new_name))
                    order_image_list.append(new_name)
            ad.order_image_list = order_image_list
            await ad.asave(update_fields=['order_image_list'])
            await user.user_adverstiments.aadd(ad)
            await self.send_notifications(user,ad)
            await sync_to_async(recommendations_to_DB.send)([{"id":user1.id,"history":[adv.id async for adv in user1.history.all()]} async for user1 in User.objects.all()],category)
            return Response({"status":"Success",'url':reverse('adv')+f'?adv_id={ad.id}'})
        return Response({"status":"ERROR"})
    async def send_notifications(self,user,ad):
        subscribed_users = [user async for user in user.subscriptions_set.all()]
        if len(subscribed_users)!=0:
            notific = Notification(Head='Появилось новое объявление',Body=f'{ad.main_name}',Timestamp = datetime.datetime.now(),Url=reverse('adv')+f'?adv_id={ad.id}')
            await notific.asave()
            payload = {'head':'Появилось новое объявление','body':f'{ad.main_name}','url':reverse('adv')+f'?adv_id={ad.id}'}
            for i in subscribed_users:
                await i.notifications.aadd(notific)
                try:
                    await sync_to_async(send_user_notification)(i,payload=payload,ttl=1200)
                except:
                    pass
class Click_Adverstiment_Logger(APIView):
    async def post(self,request):
        if request.data:
            data = request.data
            adv = await Adverstiment.objects.aget(id=data["id"])
            user = await get_user(request=request)
            if not adv:

                return Response({"status":"Unknown command"})
            if not user.is_authenticated:
                return Response({"status":"OK"})
            contain_flag = await contains_in(adv,user.history)
            if not(contain_flag):
                await user.history.aadd(adv)
                await sync_to_async(recommendations_to_DB.send)({"id":user.id,"history":[adv.id async for adv in user.history.all() ]},adv.category)
            return Response({"status":"Success"})
class ReviewAPI(APIView):
    permission_classes=[IsAuthenticated]
    async def get(self,request):
        from_user = await get_user(request)
        if not request.query_params.get('my_review',None):
            try:
                to_user = await User.objects.aget(id=request.query_params.get('id',None))
            except:
                return Response({'status':'ERROR'})
            count = int(request.query_params.get('count',0))
            reviews = [i async for i in to_user.reviews.all()[count*10:(count+1)*10] ]
            serializer = ReviewSerializer(reviews,many=True)
            ans = {'reviews':await serializer.adata,'ratings':{'5':await sync_to_async(to_user.reviews.filter(rating=5).count)(),'4':await sync_to_async(to_user.reviews.filter(rating=4).count)(),'3':await sync_to_async(to_user.reviews.filter(rating=3).count)(),'2':await sync_to_async(to_user.reviews.filter(rating=2).count)(),'1':await sync_to_async(to_user.reviews.filter(rating=1).count)()}}
            return Response(ans)
        else:
            ans = {}
            try:
                user_review = await to_user.reviews.aget(myuser__username=from_user.username)
                ans['my_review']= await ReviewSerializer(user_review).adata
            except Review.DoesNotExist:
                pass
            ans['status']='Success'
            return Response(ans)
    async def post(self,request):
        if request.data:
            data = request.data
            to_user_id = data.get("user_id",None)
            if not to_user_id:
                return Response({'status':'ERROR'})
            from_user= await get_user(request)
            if not from_user:
                return Response({'status':'ERROR','description':'WHOAREYOU'})
            from_user_id=from_user.id
            if to_user_id==from_user_id:
                return Response({"status":"ERROR"})
            rating = int(data["rating"])
            if rating<1 or rating>5:
                return Response({"status":"ERROR"})
            text = strip_tags(data["text"])
            user = await User.objects.aget(id=to_user_id)
            if not user:
                return Response({"status":"ERROR",})
            adv_id = data.get('adv_id',None)
            if not adv_id:
                return Response({'status':'ERROR'})
            
            adv = await Adverstiment.objects.aget(id=adv_id)
            rev,created = await Review.objects.aupdate_or_create(rating=rating,text=text,adverstiment = adv,wrote_by=from_user_id)
            await rev.asave()
            if created:
                await user.reviews.aadd(rev)
            return Response({"status":"Success"})
class AdverstimentSetstatus(APIView):
    permission_classes=[IsAuthenticated]
    async def post(self,request):
        user = await get_user(request)
        data =request.data
        status = data["status"]
        adv_id = data["id"]
        if status == "favorite":
                try:
                    adv = await user.related_adverstiments.aget(id=adv_id)
                    await sync_to_async(user.related_adverstiments.remove)(adv)
                    await user.asave()
                except Exception as e:
                    adv = await Adverstiment.objects.aget(id=adv_id)
                    await user.related_adverstiments.aadd(adv)
                    await user.asave()
        return Response({"status":"Success"})