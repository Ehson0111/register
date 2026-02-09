from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^auth/', views.proxy_view, name='auth-proxy'),
    re_path(r'^users/', views.proxy_view, name='users-proxy'),


    re_path(r'^contacts/.*', views.proxy_view, name='contacts-proxy'),
    re_path(r'^tasks/.*', views.proxy_view, name='tasks-proxy'),


    re_path(r'^services/', views.proxy_view, name='services-proxy'),
    re_path(r'^deals/', views.proxy_view, name='deals-proxy'),
    
    re_path(r'^marketing/', views.proxy_view, name='marketing'),
    re_path(r'^client/', views.proxy_view, name='client'),
    re_path(r'^documents/', views.proxy_view, name='documents'),
]