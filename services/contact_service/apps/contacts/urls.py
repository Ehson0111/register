# # contacts/urls.py

# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import ContactViewSet

# router = DefaultRouter()
# router.register(r'contacts', ContactViewSet, basename='contact')

# urlpatterns = [
#     path('', include(router.urls)),
# ]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .import views 

# router = DefaultRouter()
# router.register(r'contacts', views.ContactViewSet.as_view(), basename='contact')

# urlpatterns = [
#     path('', include(router.urls)),
# ]



urlpatterns = [
    path('contacts/', views.ContactlistView.as_view(), name='contact'),
]
