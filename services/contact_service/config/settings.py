 # DEFAULT_AUTOfrom pathlib import Path
from datetime import timedelta
from decouple import config  # ← pip install python-decouple
import os 
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
# SECRET_KEY = 'django-insecure-7j#3(d%=j8h(0bx9-louse(gc-ne57)dv8&l*at_9@#hh7m^=t'

# SECRET_KEY = config('SECRET_KEY', default='super-secret-jwt-key-1234567890')
SECRET_KEY = 'django-insecure-j4qv2$-!q_yfd0n&*qt^n1#mya66nqah9r3b1m1@-s!$s0pe$2'

DEBUG = True
ALLOWED_HOSTS = [
    'localhost', '127.0.0.1', '0.0.0.0',
    'contact-service', 'api-gateway', 'user-service', 'calendar', 'marketing', 'documents',
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

LOCAL_APPS = ['apps.contacts']

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
        'NAME': BASE_DIR / 'databases' / 'contact.db',  # ← contact.db
    }
}
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTStatelessUserAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# JWT Settings
# SIMPLE_JWT = {
#     'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
#     'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
#     'ROTATE_REFRESH_TOKENS': True,
# }


SIMPLE_JWT = {
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,       # используем тот же SECRET_KEY, что и в user-service
    'AUTH_HEADER_TYPES': ('Bearer',),
    # при необходимости можно явно задать USER_ID_CLAIM или другие опции
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    }


CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

WORK_PROCESS_SERVICE_URL = os.getenv("WORK_PROCESS_SERVICE_URL", "http://127.0.0.1:8011")
WORK_PROCESS_EVENT_SECRET = os.getenv(
    "WORK_PROCESS_EVENT_SECRET",
    "crm-work-process-secret-2026",
)

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'