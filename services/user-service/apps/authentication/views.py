from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from apps.users.models import User

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'error': 'Email и пароль обязательны'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=email, password=password)
    if user and user.is_active:
      refresh = RefreshToken.for_user(user)

# Добавляем данные в refresh (на всякий случай, для рефреша)
      refresh['role'] = user.role
      refresh['email'] = user.email
      refresh['first_name'] = user.first_name or ''
      refresh['last_name'] = user.last_name or ''
      
      # Создаём access-токен и вручную добавляем нужные поля в его payload
      access_token = refresh.access_token
      access_token['user_id'] = user.id  # уже есть, но на всякий
      access_token['role'] = user.role
      access_token['email'] = user.email
      access_token['first_name'] = user.first_name or ''
      access_token['last_name'] = user.last_name or ''
      
      return Response({
          'access': str(access_token),          # ← теперь с кастомными полями
          'refresh': str(refresh),
          'user': {
              'id': user.id,
              'email': user.email,
              'username': user.username,
              'first_name': user.first_name,
              'last_name': user.last_name,
              'role': user.role,
          }
      })
    return Response(
        {'error': 'Неверные данные'},
        status=status.HTTP_401_UNAUTHORIZED
    )

# @api_view(['POST'])
# @permission_classes([AllowAny])
# def refresh_token(request):
#     try:
#         refresh_token = request.data.get('refresh')
#         if not refresh_token:
#             return Response(
#                 {'error': 'Refresh token is required'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         refresh = RefreshToken(refresh_token)
#         return Response({
#             'access': str(refresh.access_token),
#         })
#     except Exception as e:
#         return Response(
#             {'error': 'Invalid refresh token'},
#             status=status.HTTP_401_UNAUTHORIZED
#         )

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=400)

        # Валидируем старый refresh
        refresh = RefreshToken(refresh_token)

        # Берём данные из старого refresh (они там есть после логина)
        role = refresh.get('role')
        email = refresh.get('email')
        first_name = refresh.get('first_name', '')
        last_name = refresh.get('last_name', '')

        # Создаём новый access и добавляем поля
        access_token = refresh.access_token
        if role:
            access_token['role'] = role
        if email:
            access_token['email'] = email
        access_token['first_name'] = first_name
        access_token['last_name'] = last_name

        return Response({
            'access': str(access_token),
        })
    except Exception as e:
        return Response({'error': 'Invalid refresh token'}, status=401)