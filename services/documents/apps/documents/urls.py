from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.DocumentUploadView.as_view(), name='document-upload'),
    path('<int:client_id>/list/', views.DocumentListView.as_view(), name='document-list'),
    path('download/<int:pk>/', views.DocumentDownloadView.as_view(), name='document-download'),
    path('delete/<int:pk>/', views.DocumentDeleteView.as_view(), name='document-delete'),
]