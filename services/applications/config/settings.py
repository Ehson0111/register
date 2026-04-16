from pathlib import Path
from datetime import timedelta

from decouple import config  # pip install python-decouple

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='dev-secret-key-change-me')
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = [
    'localhost', '127.0.0.1', '0.0.0.0',
    'calendar', 'api-gateway', 'user-service', 'contact-service', 'marketing', 'documents',
    'applications',
]

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',


]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',  # ← 
]

LOCAL_APPS = ['apps.applications']

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.applications.debug_middleware.DebugApplicationsMiddleware',
]
ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'databases' / 'applications.db',  # ← contact.db
    }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',  # простая локальная база
#     }
# }

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = config('TIME_ZONE', default='Europe/Moscow')
USE_I18N = True
USE_TZ = True

REST_FRAMEWORK = {
    # Для заявок не требуем JWT на уровне сервиса, чтобы не было 401 на просроченном токене.
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    # плюс наши фильтры/пагинация для удобства
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': config(
        'JWT_SIGNING_KEY',
        default='django-insecure-j4qv2$-!q_yfd0n&*qt^n1#mya66nqah9r3b1m1@-s!$s0pe$2'
    ),
}


CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
 
# IMAP / Yandex Mail parser
YANDEX_IMAP_HOST = config('YANDEX_IMAP_HOST', default='imap.yandex.ru')
YANDEX_EMAIL = config('YANDEX_EMAIL', default='ehsonboboev7@yandex.ru')
YANDEX_PASSWORD = config('YANDEX_PASSWORD', default='hbewwdgiloviutid')
YANDEX_TARGET_SENDER = config('YANDEX_TARGET_SENDER', default='69aeaa09eb6146cd4fd99c6b@forms.yandex.com')
YANDEX_SMTP_HOST = config('YANDEX_SMTP_HOST', default='smtp.yandex.ru')
YANDEX_SMTP_PORT = config('YANDEX_SMTP_PORT', default=465, cast=int)
YANDEX_SMTP_USE_SSL = config('YANDEX_SMTP_USE_SSL', default=True, cast=bool)


# YANDEX_IMAP_HOST = config('YANDEX_IMAP_HOST', default='imap.yandex.ru')
# YANDEX_EMAIL = config('YANDEX_EMAIL', default='ehsonboboev7@yandex.ru')
# YANDEX_PASSWORD = config('YANDEX_PASSWORD', default='hbewwdgiloviutid')
# YANDEX_TARGET_SENDER = config('YANDEX_TARGET_SENDER', default='69aeaa09eb6146cd4fd99c6b@forms.yandex.com')

