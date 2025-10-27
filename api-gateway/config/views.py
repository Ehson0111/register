import requests
from django.http import JsonResponse

def proxy_login(request):
    try:
        response = requests.post('http://user-service:8001/login/', data=request.POST)
        return JsonResponse(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)