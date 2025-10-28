# apps/gateway/urls.py
from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    re_path(r'^auth/.*', csrf_exempt(views.proxy_view), name='auth-proxy'),
    re_path(r'^users/.*', csrf_exempt(views.proxy_view), name='users-proxy'),
]