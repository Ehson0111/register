from django.urls import path,re_path
from . import views
 


urlpatterns = [
    re_path(r'^auth/.*',views.proxy_view, name='auth-proxy'),
    re_path(r'^users/.*', views.proxy_view, name='users-proxy'),

]
