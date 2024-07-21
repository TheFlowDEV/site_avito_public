from adrf import serializers
from django.contrib.auth import get_user_model
from rest_framework import serializers as drf_serializers
from django.apps import apps
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
Message = apps.get_model('TPUvito',"Message")
User = get_user_model()
Review = apps.get_model('users','Review')
Adverstiment = apps.get_model('users','Adverstiment')
Notification = apps.get_model('users','Notification')
class ADRFPrimaryKeyRelatedField(drf_serializers.RelatedField):
    default_error_messages = {
        'required': ('This field is required.'),
        'does_not_exist': ('Invalid pk "{pk_value}" - object does not exist.'),
        'incorrect_type': ('Incorrect type. Expected pk value, received {data_type}.'),
    }

    def __init__(self, **kwargs):
        self.pk_field = kwargs.pop('pk_field', None)
        super().__init__(**kwargs)

    def use_pk_only_optimization(self):
        return True

    def to_internal_value(self, data):
        if self.pk_field is not None:
            data = self.pk_field.to_internal_value(data)
        queryset = self.get_queryset()
        try:
            if isinstance(data, bool):
                raise TypeError
            return queryset.get(pk=data)
        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)

    def to_representation(self, value):
        if self.pk_field is not None:
            return self.pk_field.to_representation(value.pk)
        return value.pk
    async def ato_representation(self,value):
        if self.pk_field is not None:
            return await sync_to_async(self.pk_field.to_representation)(value.pk)
        return value.pk
class ADRFSerializerMethodField(drf_serializers.Field):
    def __init__(self, method_name=None, **kwargs):
        self.method_name = method_name
        kwargs['source'] = '*'
        kwargs['read_only'] = True
        super().__init__(**kwargs)

    def bind(self, field_name, parent):
        if self.method_name is None:
            self.method_name = 'get_{field_name}'.format(field_name=field_name)
        super().bind(field_name, parent)
    async def ato_representation(self,value):
        method = await sync_to_async(getattr)(self.parent, self.method_name)
        return await method(value)

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
    adverstiment=ADRFPrimaryKeyRelatedField(read_only=True)
    adverstiment_name = ADRFSerializerMethodField()
    user_photo = ADRFSerializerMethodField()
    user_username = ADRFSerializerMethodField()
    async def get_user_username(self,obj):
        user = await User.objects.aget(id=obj.wrote_by)
        return user.username
    async def get_user_photo(self,obj):
        user = await User.objects.aget(id=obj.wrote_by)
        return user.photo
    async def get_adverstiment_name(self,obj):
        adv = await self.get_adverstiment(obj)
        return adv.main_name
    @sync_to_async
    def get_adverstiment(self,obj):
        return obj.adverstiment
class AdverstimentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Adverstiment
        fields=['id','main_name','category','cost','university_from','is_active','sold_by','photo','datetime','is_favorite']
    async def get_photo(self,obj):
        return obj.get_photo(self.context['one'])
    async def get_datetime(self,obj):
        return obj.datetime.strftime("%m/%d, %H:%M:%S")
    async def get_sold_by(self,obj):
        sold_by_user =await obj.user_advs.afirst()
        if not sold_by_user:
            return '????'
        return sold_by_user.username
    async def get_university_from(self,obj):
        sold_by_user =await obj.user_advs.afirst()
        if not sold_by_user:
            return '????'
        return sold_by_user.university
    async def get_is_favorite(self,obj):
        request_user = self.context['request_user']
        sold_by_user =await obj.user_advs.afirst()
        print(obj.main_name)
        if not sold_by_user:
            return '????'
        if request_user.is_authenticated:
            try:
                if await request_user.related_adverstiments.aget(id = obj.id):
                    return True
            except Exception as e:
                print(e,request_user,sold_by_user)
                if request_user!=sold_by_user:
                    return False
    photo = ADRFSerializerMethodField()
    datetime = ADRFSerializerMethodField()
    sold_by = ADRFSerializerMethodField()
    university_from = ADRFSerializerMethodField()
    is_favorite = ADRFSerializerMethodField()
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Notification
        exclude=('Read',)
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model=Message
        fields =['type','text','timestamp','username','you']
    username =  ADRFSerializerMethodField()
    you = ADRFSerializerMethodField()
    async def get_username(self,obj):
        user = await sync_to_async(lambda:obj.user)()
        return await sync_to_async(user.get_username)()
    async def get_you(self,obj):
        user = await sync_to_async(lambda:obj.user)()
        request_user = self.context['request_user']
        return user==request_user