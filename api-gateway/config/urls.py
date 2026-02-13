from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'service': 'api-gateway',
        'services': {
            'user-service': 'http://localhost:8000',
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.gateway.urls')),
    path('health/', health_check),  # 
]