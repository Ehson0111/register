import random
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from .models import EmailOTP


def _generate_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def _issue_otp(email: str, purpose: str) -> EmailOTP:
    # Invalidate previous unused codes of same purpose
    EmailOTP.objects.filter(email=email, purpose=purpose, used=False).update(used=True)
    code = _generate_code()
    ttl = getattr(settings, "OTP_CODE_TTL_SECONDS", 600)
    otp = EmailOTP.objects.create(
        email=email,
        purpose=purpose,
        code=code,
        expires_at=timezone.now() + timedelta(seconds=ttl),
        used=False,
    )
    return otp


def _send_code_email(email: str, subject: str, code: str):
    send_mail(
        subject=subject,
        message=f"Ваш код: {code}\n\nКод действует ограниченное время.",
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=[email],
        fail_silently=False,
    )

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
      if getattr(user, 'role', None) not in (User.ROLE_MANAGER, User.ROLE_ADMIN):
          return Response(
              {'error': 'Вход доступен только менеджерам и администраторам CRM'},
              status=status.HTTP_403_FORBIDDEN,
          )
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


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_request(request):
    """
    Запрос на сброс пароля.
    Всегда возвращает success=true (чтобы не раскрывать существование email).
    """
    email = (request.data.get("email") or "").strip().lower()
    if not email:
        return Response({"error": "Email обязателен"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        otp = _issue_otp(email=email, purpose=EmailOTP.PURPOSE_RESET)
        _send_code_email(email=email, subject="Сброс пароля", code=otp.code)

    return Response({"success": True, "message": "Если email существует, код отправлен на почту."})


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """
    Подтверждение сброса пароля по коду (6 цифр) и установка нового пароля.
    """
    email = (request.data.get("email") or "").strip().lower()
    code = (request.data.get("code") or "").strip()
    new_password = request.data.get("new_password") or ""
    new_password_confirm = request.data.get("new_password_confirm") or ""

    if not email or not code:
        return Response({"error": "Email и code обязательны"}, status=status.HTTP_400_BAD_REQUEST)
    if not new_password or not new_password_confirm:
        return Response({"error": "Новый пароль и подтверждение обязательны"}, status=status.HTTP_400_BAD_REQUEST)
    if new_password != new_password_confirm:
        return Response({"error": "Пароли не совпадают"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        otp = EmailOTP.objects.filter(
            email=email, purpose=EmailOTP.PURPOSE_RESET, used=False
        ).order_by("-created_at").first()
        if not otp:
            return Response({"error": "Код не найден"}, status=status.HTTP_400_BAD_REQUEST)
        if otp.is_expired():
            otp.used = True
            otp.save(update_fields=["used"])
            return Response({"error": "Код истёк"}, status=status.HTTP_400_BAD_REQUEST)

        max_attempts = getattr(settings, "OTP_MAX_ATTEMPTS", 5)
        if otp.attempts >= max_attempts:
            otp.used = True
            otp.save(update_fields=["used"])
            return Response({"error": "Слишком много попыток. Запросите новый код."}, status=status.HTTP_400_BAD_REQUEST)

        if otp.code != code:
            otp.attempts += 1
            otp.save(update_fields=["attempts"])
            return Response({"error": "Неверный код"}, status=status.HTTP_400_BAD_REQUEST)

        # validate password
        try:
            validate_password(new_password)
        except exceptions.ValidationError as e:
            return Response({"error": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save(update_fields=["password"])

        otp.used = True
        otp.save(update_fields=["used"])

        return Response({"success": True, "message": "Пароль обновлён"})

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)