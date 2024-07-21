from typing import Any
from django.contrib.auth.backends import ModelBackend
from .models import MyUser
from django.db.models import Q
class EmailBackend(ModelBackend):
    def authenticate(self,request,password,username="",email="", **kwargs: Any) -> MyUser | None:
        
        try:
            user = MyUser.objects.get(Q(email__iexact=email)|Q(username__iexact=username))
        except MyUser.DoesNotExist:
            return None
        except MyUser.MultipleObjectsReturned:
            return None
        else:

            if user.check_password(raw_password=password) and self.user_can_authenticate(user):
                return user
        return None
    def get_user(self, user_id):
        try:
            user = MyUser.objects.get(pk=user_id)
        except MyUser.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None