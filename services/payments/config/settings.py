from datetime import timedelta
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-j4qv2$-!q_yfd0n&*qt^n1#mya66nqah9r3b1m1@-s!$s0pe$2'

YOOKASSA_SHOP_ID = '1335151'
YOOKASSA_SECRET_KEY = 'test_3RDrQQ3KHo_QzYn9jw0orffJb1u8ILESiNzOfuIyi4I'

CONTACT_SERVICE_URL = os.getenv('CONTACT_SERVICE_URL', 'http://127.0.0.1:8005')
PUBLIC_PAYMENTS_BASE_URL = os.getenv('PUBLIC_PAYMENTS_BASE_URL', 'https://incessantly-golden-gannet.cloudpub.ru')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'no-reply@crm.local')

ONEC_BASE_URL = os.getenv('ONEC_BASE_URL', 'http://host.docker.internal/1c/odata/standard.odata/')
ONEC_ODATA_BASE_URL = os.getenv('ONEC_ODATA_BASE_URL', ONEC_BASE_URL)
ONEC_CREATE_INVOICE_URL = os.getenv('ONEC_CREATE_INVOICE_URL', ONEC_ODATA_BASE_URL)
ONEC_MARK_PAID_URL = os.getenv('ONEC_MARK_PAID_URL', ONEC_ODATA_BASE_URL)
ONEC_USERNAME = os.getenv('ONEC_USERNAME', '')
ONEC_PASSWORD = os.getenv('ONEC_PASSWORD', '')
ONEC_TIMEOUT_SECONDS = int(os.getenv('ONEC_TIMEOUT_SECONDS', '20'))
ONEC_TRANSPORT_MODE = os.getenv('ONEC_TRANSPORT_MODE', 'bridge')
ONEC_BRIDGE_URL = os.getenv('ONEC_BRIDGE_URL', 'http://127.0.0.1:8013/invoke')
ONEC_BRIDGE_SECRET = os.getenv('ONEC_BRIDGE_SECRET', '')
ONEC_BRIDGE_TIMEOUT_SECONDS = int(os.getenv('ONEC_BRIDGE_TIMEOUT_SECONDS', '60'))
ONEC_RESTART_EACH_REQUEST = os.getenv('ONEC_RESTART_EACH_REQUEST', 'true').lower() == 'true'  # РђРІС‚РѕРјР°С‚РёС‡РµСЃРєРёР№ РїРµСЂРµР·Р°РїСѓСЃРє IIS РїРµСЂРµРґ РєР°Р¶РґС‹Рј Р·Р°РїСЂРѕСЃРѕРј (РґР»СЏ СѓС‡РµР±РЅРѕР№ РІРµСЂСЃРёРё 1РЎ)
ONEC_RESTART_COMMAND = os.getenv('ONEC_RESTART_COMMAND', 'iisreset')
ONEC_RESTART_TIMEOUT_SECONDS = int(os.getenv('ONEC_RESTART_TIMEOUT_SECONDS', '30'))
ONEC_MAX_RETRIES = int(os.getenv('ONEC_MAX_RETRIES', '3'))
ONEC_HEALTHCHECK_PATH = os.getenv('ONEC_HEALTHCHECK_PATH', '$metadata')
ONEC_HEALTH_TIMEOUT_SECONDS = int(os.getenv('ONEC_HEALTH_TIMEOUT_SECONDS', '45'))
ONEC_HEALTHCHECK_TIMEOUT_SECONDS = int(os.getenv('ONEC_HEALTHCHECK_TIMEOUT_SECONDS', '10'))
ONEC_HEALTHCHECK_INTERVAL_SECONDS = float(os.getenv('ONEC_HEALTHCHECK_INTERVAL_SECONDS', '2'))
ONEC_ORGANIZATION_KEY = os.getenv('ONEC_ORGANIZATION_KEY', '')
ONEC_PAYMENT_INVOICE_FIELD = os.getenv('ONEC_PAYMENT_INVOICE_FIELD', 'РЎС‡РµС‚_Key')
ONEC_STATUS_UNPAID_VALUE = os.getenv('ONEC_STATUS_UNPAID_VALUE', 'РќРµРћРїР»Р°С‡РµРЅ')
ONEC_STATUS_PAID_VALUE = os.getenv('ONEC_STATUS_PAID_VALUE', 'РћРїР»Р°С‡РµРЅ')
ONEC_DEFAULT_CUSTOMER_TYPE = os.getenv('ONEC_DEFAULT_CUSTOMER_TYPE', 'crm')
ONEC_DEFAULT_PAYMENT_METHOD = os.getenv('ONEC_DEFAULT_PAYMENT_METHOD', 'yookassa')
ONEC_SERVICE_UNIT = os.getenv('ONEC_SERVICE_UNIT', 'С€С‚')
ONEC_SERVICE_ACTIVITY = os.getenv('ONEC_SERVICE_ACTIVITY', 'РђРєС‚РёРІРЅР°')
ONEC_AUTO_POST_DOCUMENTS = os.getenv('ONEC_AUTO_POST_DOCUMENTS', 'false').lower() == 'true'
ONEC_POSTING_MODE_OPERATIONAL = os.getenv('ONEC_POSTING_MODE_OPERATIONAL', 'false').lower() == 'true'
INVOICE_RETRY_WORKER_INTERVAL_SECONDS = int(os.getenv('INVOICE_RETRY_WORKER_INTERVAL_SECONDS', '30'))



# РќР°СЃС‚СЂРѕР№РєР° РїР»Р°С‚РµР¶РЅРѕРіРѕ РїСЂРѕРІР°Р№РґРµСЂР°
PAYMENT_VARIANTS = {
    'yookassa': ('django_payments_yookassa.YooKassaProvider', {
        'shop_id': YOOKASSA_SHOP_ID,
        'secret_key': YOOKASSA_SECRET_KEY,
        'capture': True,          
        'use_webhook': True,      
        'test_mode': True,            
    }),
}   

DEBUG = True
_public_payments_host = (
    PUBLIC_PAYMENTS_BASE_URL
    .replace('https://', '')
    .replace('http://', '')
    .rstrip('/')
)
_extra_allowed_hosts = [
    host.strip()
    for host in os.getenv('PAYMENTS_ALLOWED_HOSTS', '').split(',')
    if host.strip()
]
ALLOWED_HOSTS = [
    'localhost', '127.0.0.1', '0.0.0.0',
    'marketing', 'api-gateway', 'user-service', 'contact-service', 'calendar', 'documents', 'payments',
    _public_payments_host,
    *_extra_allowed_hosts,
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
    'django_filters',
]
 

_extra_csrf_trusted_origins = [
    origin.strip()
    for origin in os.getenv('PAYMENTS_CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]
CSRF_TRUSTED_ORIGINS = [PUBLIC_PAYMENTS_BASE_URL, *_extra_csrf_trusted_origins]


LOCAL_APPS = ['apps.yookassa_integration']

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
AUTH_USER_MODEL = 'auth.User'


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
        'NAME': BASE_DIR / 'db.sqlite3',
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



SIMPLE_JWT = {
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,       # РёСЃРїРѕР»СЊР·СѓРµРј С‚РѕС‚ Р¶Рµ SECRET_KEY, С‡С‚Рѕ Рё РІ user-service
    'AUTH_HEADER_TYPES': ('Bearer',),
    # РїСЂРё РЅРµРѕР±С…РѕРґРёРјРѕСЃС‚Рё РјРѕР¶РЅРѕ СЏРІРЅРѕ Р·Р°РґР°С‚СЊ USER_ID_CLAIM РёР»Рё РґСЂСѓРіРёРµ РѕРїС†РёРё
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    }


CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '25'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'false').lower() == 'true'

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
