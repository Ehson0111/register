from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('refresh/', views.refresh_token, name='refresh'),
    path('password-reset/request/', views.password_reset_request, name='password-reset-request'),
    path('password-reset/confirm/', views.password_reset_confirm, name='password-reset-confirm'),
]
