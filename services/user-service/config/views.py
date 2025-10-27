from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Простая проверка (замените на реальную логику, например, Django auth)
        if username == 'admin' and password == 'password':
            return JsonResponse({'success': True, 'message': 'Login successful'})
        return JsonResponse({'success': False, 'message': 'Invalid credentials'}, status=401)
    return JsonResponse({'error': 'Method not allowed'}, status=405)