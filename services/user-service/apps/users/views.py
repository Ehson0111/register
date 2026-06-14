import logging
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User, UserProfile
from .permissions import IsManagerOrAdmin, IsAdmin
from .serializers import (
    UserWithProfileSerializer,
    UserProfileSerializer,
    UserListSerializer,
    StaffCreateUserSerializer,
    StaffUserActiveSerializer,
    StaffUserRoleSerializer,
    StaffUserPasswordSerializer,
    ProfilePasswordChangeSerializer,
)

logger = logging.getLogger(__name__)


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


class ProfilePasswordChangeView(generics.GenericAPIView):
    """Смена пароля текущего пользователя."""

    permission_classes = [IsAuthenticated, IsManagerOrAdmin]
    serializer_class = ProfilePasswordChangeSerializer
    http_method_names = ['patch', 'head', 'options']

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info("Profile password changed for user id=%s email=%s", request.user.id, request.user.email)
        return Response({'success': True, 'message': 'Пароль обновлён'})


class StaffUserListCreateView(generics.ListCreateAPIView):
    """
    GET — список пользователей (менеджер/админ, для чатов и панели).
    POST — создание сотрудника (только администратор; роли admin/manager).
    """

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated(), IsManagerOrAdmin()]

    def get_queryset(self):
        return User.objects.filter(role__in=[User.ROLE_ADMIN, User.ROLE_MANAGER]).order_by('-date_joined')

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


class StaffUserRoleUpdateView(generics.UpdateAPIView):
    """Смена роли пользователя — только администратор."""

    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.objects.all()
    serializer_class = StaffUserRoleSerializer
    http_method_names = ['patch', 'head', 'options']

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class StaffUserPasswordUpdateView(generics.GenericAPIView):
    """Смена пароля менеджера — только администратор."""

    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.objects.all()
    serializer_class = StaffUserPasswordSerializer
    http_method_names = ['patch', 'head', 'options']

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.role != User.ROLE_MANAGER:
            return Response(
                {'detail': 'Пароль можно менять только у менеджеров.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(
            data=request.data,
            context={'request': request, 'user': instance},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info("Admin changed password for manager id=%s email=%s", instance.id, instance.email)
        return Response({'success': True, 'message': 'Пароль обновлён'})


class StaffUserDestroyView(generics.DestroyAPIView):
    """Удаление менеджера — только администратор (не себя и не других админов)."""

    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.objects.all()
    http_method_names = ['delete', 'head', 'options']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.pk == request.user.pk:
            return Response(
                {'detail': 'Нельзя удалить свою учётную запись.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if instance.role == User.ROLE_ADMIN:
            return Response(
                {'detail': 'Нельзя удалить администратора.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if instance.role != User.ROLE_MANAGER:
            return Response(
                {'detail': 'Удалять можно только учётные записи менеджеров.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.info("Admin deleted manager id=%s email=%s", instance.id, instance.email)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
