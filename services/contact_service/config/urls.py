# from django.contrib import admin
# from django.urls import path, include
# from django.http import JsonResponse

# def health_check(request):
#     return JsonResponse({'status': 'healthy', 'service': 'contact-service'})

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('health/', health_check),
#     path('api/contacts/', include('apps.contacts.urls')),
# ]
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'contact-service'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check),
    path('api/', include('apps.contacts.urls')),
]