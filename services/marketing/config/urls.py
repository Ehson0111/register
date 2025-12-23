from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    """Health check endpoint for monitoring."""
    return JsonResponse({'status': 'healthy', 'service': 'marketing-service'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check),
    path('api/', include('apps.marketing.urls')),
]