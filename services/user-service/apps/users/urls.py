from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('register/verify/', views.VerifyRegistrationView.as_view(), name='register-verify'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile-update'),
    path('profile/change-password/', views.ProfilePasswordChangeView.as_view(), name='profile-change-password'),
    path('team/', views.StaffUserListCreateView.as_view(), name='user-team-list-create'),
    path('team/<int:pk>/', views.StaffUserActiveUpdateView.as_view(), name='user-team-active'),
    path('team/<int:pk>/role/', views.StaffUserRoleUpdateView.as_view(), name='user-team-role'),
    path('team/<int:pk>/delete/', views.StaffUserDestroyView.as_view(), name='user-team-delete'),
    path('team/<int:pk>/password/', views.StaffUserPasswordUpdateView.as_view(), name='user-team-password'),
]
