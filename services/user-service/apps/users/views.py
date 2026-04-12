import random
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User, UserProfile
from .permissions import IsManagerOrAdmin, IsAdmin
from .serializers import (
    UserWithProfileSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    UserListSerializer,
    StaffCreateUserSerializer,
    StaffUserActiveSerializer,
)

import logging
logger = logging.getLogger(__name__)


def _generate_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def _send_code_email(email: str, code: str):
    send_mail(
        subject="Подтверждение регистрации",
        message=f"Ваш код подтверждения: {code}\n\nКод действует ограниченное время.",
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=[email],
        fail_silently=False,
    )


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info(f"Registration attempt with data: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Require email verification
            user.is_active = False
            user.save(update_fields=["is_active"])

            # Create / replace OTP stored in DB (reuse EmailOTP from authentication app)
            from apps.authentication.models import EmailOTP

            EmailOTP.objects.filter(email=user.email, purpose=EmailOTP.PURPOSE_REGISTER, used=False).update(used=True)
            ttl = getattr(settings, "OTP_CODE_TTL_SECONDS", 600)
            code = _generate_code()
            EmailOTP.objects.create(
                email=user.email,
                purpose=EmailOTP.PURPOSE_REGISTER,
                code=code,
                expires_at=timezone.now() + timedelta(seconds=ttl),
                used=False,
            )
            _send_code_email(user.email, code)

            logger.info(f"User registered (inactive), verification sent: {user.email}")
            return Response({
                'success': True,
                'message': 'Код подтверждения отправлен на почту',
                'verification_required': True,
                'email': user.email,
                'user_id': user.id,
            }, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Registration validation errors: {serializer.errors}")
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class VerifyRegistrationView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = (request.data.get("email") or "").strip().lower()
        code = (request.data.get("code") or "").strip()
        if not email or not code:
            return Response({"error": "Email и code обязательны"}, status=status.HTTP_400_BAD_REQUEST)

        from apps.authentication.models import EmailOTP

        otp = EmailOTP.objects.filter(
            email=email, purpose=EmailOTP.PURPOSE_REGISTER, used=False
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

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save(update_fields=["is_active"])
        otp.used = True
        otp.save(update_fields=["used"])

        return Response({"success": True, "message": "Email подтверждён. Теперь можно войти."})
    
class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserWithProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class ProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class StaffUserListCreateView(generics.ListCreateAPIView):
    """
    Список пользователей и создание: менеджер — только клиенты; администратор — менеджеры и клиенты.
    """

    permission_classes = [IsAuthenticated, IsManagerOrAdmin]

    def get_queryset(self):
        return User.objects.all().order_by('-date_joined')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return StaffCreateUserSerializer
        return UserListSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.info("Staff created user id=%s email=%s role=%s", user.id, user.email, user.role)
        out = UserListSerializer(user, context={'request': request})
        return Response(out.data, status=status.HTTP_201_CREATED)


class StaffUserActiveUpdateView(generics.UpdateAPIView):
    """Включение/отключение учётной записи — только администратор."""

    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.objects.all()
    serializer_class = StaffUserActiveSerializer
    http_method_names = ['patch', 'head', 'options']

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx
