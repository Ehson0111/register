# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from . import views

# router = DefaultRouter()

# router.register(r'templates', views.TemplateViewSet, basename='template')
# router.register(r'campaigns', views.CampaignViewSet, basename='campaign')

# urlpatterns = [
#     path('',include(router.urls)),

#     path('send-campaign/', views.SendCampaignView.as_view(), name='send-campaign'),
#     path('send-individual/', views.IndividualSendView.as_view(), name='send-individual'),
#     path('history/', views.CampaignHistoryView.as_view(), name='campaign-history'),
# ]


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r'templates', views.TemplateViewSet, basename='template')
router.register(r'campaigns', views.CampaignViewSet, basename='campaign')

urlpatterns = [
    path('',include(router.urls)),
    
    path('send-campaign/', views.SendCampaignView.as_view(), name='send-campaign'),
    path('send-individual/', views.IndividualSendView.as_view(), name='send-individual'),
    path('send-quick-message/', views.QuickMessageView.as_view(), name='send-quick-message'),
    path('history/', views.CampaignHistoryView.as_view(), name='campaign-history'),
]