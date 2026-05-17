from django.urls import path, include

urlpatterns = [ 
    path('api/payment/', include('apps.yookassa_integration.urls')),
    path('payment/', include('apps.yookassa_integration.urls')),
]