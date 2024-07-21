from django.apps import AppConfig
from django.db import connection
from sys import platform

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    if platform=="linux" or platform=="linux2":
        path="/home/user1/studentmarket/users"
    def ready(self) -> None:
        super().ready()
        with connection.cursor() as cursor:
            cursor.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')
            cursor.execute('CREATE EXTENSION IF NOT EXISTS unaccent;')