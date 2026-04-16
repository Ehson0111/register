from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'applications', views.ApplicationsViewSet, basename='applications')

urlpatterns = [
    path('', include(router.urls)),
    path('mail/', views.MailboxEmailListView.as_view(), name='mail-list'),
    path('mail/folders/', views.MailboxFoldersView.as_view(), name='mail-folders'),
    path('mail/sync/', views.MailboxSyncView.as_view(), name='mail-sync'),
    path('mail/send/', views.MailboxSendView.as_view(), name='mail-send'),
    path('mail/<int:pk>/', views.MailboxEmailDetailView.as_view(), name='mail-detail'),
]