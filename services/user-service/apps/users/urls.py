from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('register/verify/', views.VerifyRegistrationView.as_view(), name='register-verify'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile-update'),
    path('team/', views.StaffUserListCreateView.as_view(), name='user-team-list-create'),
    path('team/<int:pk>/', views.StaffUserActiveUpdateView.as_view(), name='user-team-active'),
]
