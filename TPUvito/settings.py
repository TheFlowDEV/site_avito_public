from pathlib import Path
import os
import sys

from authlib.integrations.django_client import OAuth
oauth =  OAuth()
oauth.register(
    name='TPU',
    client_id='129',
    client_secret=os.getenv("TPU_TOKEN"),
    access_token_url='https://oauth.tpu.ru/access_token',
    access_token_params=None,
    authorize_url='https://oauth.tpu.ru/authorize',
    authorize_params=None,
    client_kwargs=None,
)
CSRF_TRUSTED_ORIGINS = [
    'https://127.0.0.1',
    'https://oauth.tpu.ru',
    'https://oauth.vk.com'
]
secret_key_vk=os.getenv("VK_TOKEN")
oauth.register(
    name='VK',
    client_id='51916233',
    client_secret=os.getenv("VK_TOKEN"),
    access_token_url='https://oauth.vk.com/access_token',
    access_token_params=None,
    authorize_url='https://oauth.vk.com/authorize',
    authorize_params=None,
    client_kwargs=None,

)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
    }
}
CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
)

CORS_ALLOW_METHODS = (
    "GET",
    "POST"
)
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


FIELD_ENCRYPTION_KEY = os.getenv("FIELD_KEY")
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['*']
MEDIA_ROOT = BASE_DIR/'media'
MEDIA_URL = '/media/'
PRODUCT_CATEGORIES=['Одежда','Канцелярия','Товары для дома','Электроника','Хобби и творчество','Украшения и бижутерия','Здоровье','Бытовая техника','Разное']
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            'level':'INFO'
        },
        'debug_file':{
            'class':'logging.FileHandler',
            'filename':str(BASE_DIR/'debug.log'),
            "level": "DEBUG",
        },
        'error_file':{
            'class':'logging.FileHandler',
            'filename':str(BASE_DIR/'error.log'),
            "level": "ERROR",
        }
    },
    "root": {
        "handlers": ["console",'debug_file','error_file'],
        
    },
}
# Application definition

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication'
    ]
}

INSTALLED_APPS = [
    "corsheaders",
     "django_dramatiq",
     'rest_framework_simplejwt.token_blacklist',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.postgres',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'daphne',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',
     'webpack_loader',
     'channels',
     'encrypted_model_fields',
     'TPUvito',
     'webpush',
     "django_user_agents"
]
TIME_ZONE = 'Asia/Novosibirsk'
USE_TZ = True
if DEBUG:
    STATICFILES_DIRS = [
    BASE_DIR / "static"
    ]
    STATIC_DIR = BASE_DIR/'static'
# STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = '/static/'

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'webpack_bundles/',
        'CACHE': not DEBUG,
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
    }
}
AUTH_USER_MODEL = 'users.MyUser'
DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.redis.RedisBroker",
    "OPTIONS": {
        "url": "redis://localhost:6379",
    },
    "MIDDLEWARE": [

        "dramatiq.middleware.AsyncIO",
        "dramatiq.middleware.Prometheus",
        "dramatiq.middleware.AgeLimit",
        "dramatiq.middleware.TimeLimit",
        "dramatiq.middleware.Callbacks",
        "dramatiq.middleware.Retries",
        "django_dramatiq.middleware.DbConnectionsMiddleware",
        "django_dramatiq.middleware.AdminMiddleware",
    ]
}

# Defines which database should be used to persist Task objects when the
# AdminMiddleware is enabled.  The default value is "default".
DRAMATIQ_TASKS_DATABASE = "default"
MIDDLEWARE = [
     "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django.middleware.gzip.GZipMiddleware",
     'django_user_agents.middleware.UserAgentMiddleware'
]

ROOT_URLCONF = 'TPUvito.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ASGI_APPLICATION = 'TPUvito.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'TPUvito.ChannelLayer.ExtendedRedisChannelLayer',
        'CONFIG': {
            "hosts": [("localhost",6379)],
            "symmetric_encryption_keys": [SECRET_KEY],
        },
    },
}

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django',
        'USER': 'postgres',
        'PASSWORD': 'zjsjI3Km4b2kK~!E',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": "BDPh3nLJdfZO7TfLYovL-jkonoLX0C789TYNc88NuT9Mp7b92wDUcikR4vNClQUUht_Wt1C_iySfozTEUBGqAzU",
    "VAPID_PRIVATE_KEY":"fZnesha4EJTs1k6JRXKIUnbzsy79rHJ0PetZSxdO-NE",
    "VAPID_ADMIN_EMAIL": "vag57@tpu.ru"
}
# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ru'


USE_I18N = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTHENTICATION_BACKENDS = ('users.backend.EmailBackend',)

# HTTPS && SSL FIXME
#SECURE_PROXY_SSL_HEADER = ( 'HTTP_X_FORWARDED_PROTO' , 'https' )
#SECURE_SSL_REDIRECT = True
#MAKE WITH NGINX
