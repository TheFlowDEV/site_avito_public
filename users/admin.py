from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.apps import apps
from .models import MyUser as CustomUser
from .models import Adverstiment
from django.contrib.admin.models import LogEntry

Report = apps.get_model("TPUvito",'Report')

@admin.register(LogEntry)
class CustomLogEntry(admin.ModelAdmin):
    readonly_fields = ('content_type', 'user', 'action_time')
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username',)
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display=('Head','Description','Timestamp')
@admin.register(Adverstiment)
class AdverstimentAdmin(admin.ModelAdmin):
    list_display=('main_name','category')
admin.site.register(CustomUser, CustomUserAdmin)
