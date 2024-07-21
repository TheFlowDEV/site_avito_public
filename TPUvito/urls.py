"""
URL configuration for TPUvito project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from django.views.static import serve
from . import views
from . import api_views
from . import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
debug_media = [
     re_path(r'^static/(?P<path>.*)$', serve, {
            'document_root': settings.STATIC_ROOT if not settings.DEBUG else settings.STATIC_DIR,
        }),
    re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        })
] if settings.DEBUG else []
urlpatterns = [
    path('',views.index,name="index"),
    path("admin",admin.site.urls),
    path("adverstiment",views.adverstiment,name='adv'),
    path("profile",views.profile),
    path("chat",views.chat,name="chat"),
    path("chatTo<str:user_id>_<str:adv_id>",views.chat,name="chat_exact"),
    path("bind_oauth",views.bind_oauth,name="bind_oauth"),
    path("api/login_register",api_views.Login_Register.as_view()),
    path("api/add_adv",api_views.Add_Adverstiment.as_view()),
    path("api/get_adv",api_views.GetAdverstiments.as_view()),
    path("api/click_adv",api_views.Click_Adverstiment_Logger.as_view()),
    path("api/history_get",api_views.HistoryGetter.as_view()),
    path("api/adv_status_set",api_views.AdverstimentSetstatus.as_view()),
    path("api/review",api_views.ReviewAPI().as_view()),
    path("api/chat",api_views.Chat_API().as_view()),
    path('webpush/', include('webpush.urls')),
    path('api/update_adv',api_views.UpdateAdverstiment().as_view()),
    path('api/report',api_views.ReportHandler().as_view()),
    path('api/notifications',api_views.NotificationGetter().as_view()),
    path('add_adv',views.add_adv),
    path('api/changeusr',api_views.ChangeUserData().as_view()),
    path('api/refresh_token',TokenRefreshView.as_view()),
    path('api/subscribe',api_views.Subscribe().as_view()),
    path('api/ban',api_views.Ban().as_view()),
    path('api/change_passwd',api_views.ChangePassword().as_view()),
    path('login_TPU',views.login_TPU),
    path('authorize_TPU',views.authenticate_TPU),
    path('authorize_VK',views.authenticate_vk)]+debug_media


