from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from .models import User, UserProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
            'is_active', 'date_joined']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'date_of_birth']

class UserWithProfileSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name',
                  'last_name', 'is_active', 'date_joined', 'profile', 'role']


class UserListSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'role', 'role_display', 'is_active', 'date_joined',
        ]


class StaffCreateUserSerializer(serializers.ModelSerializer):
    """Создание сотрудника CRM: только администратор; роли — администратор или менеджер."""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
        choices=[User.ROLE_ADMIN, User.ROLE_MANAGER],
        help_text='Доступны только роли администратора и менеджера.',
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password_confirm', 'role']

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Пароли не совпадают"})
        try:
            validate_password(attrs['password'])
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        role = attrs.get('role')
        if role not in (User.ROLE_ADMIN, User.ROLE_MANAGER):
            raise serializers.ValidationError({'role': 'Можно назначить только администратора или менеджера.'})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        role = validated_data.pop('role')
        user = User.objects.create_user(**validated_data)
        user.role = role
        user.is_active = True
        user.save(update_fields=['role', 'is_active'])
        UserProfile.objects.get_or_create(user=user)
        return user


class StaffUserActiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['is_active']

    def validate(self, attrs):
        request = self.context.get('request')
        instance = self.instance
        if (
            instance
            and request
            and request.user.is_authenticated
            and instance.pk == request.user.pk
            and attrs.get('is_active') is False
        ):
            raise serializers.ValidationError(
                {'is_active': 'Нельзя отключить свою учётную запись.'}
            )
        return attrs


class StaffUserRoleSerializer(serializers.ModelSerializer):
    """Смена роли сотрудника — только администратор; только admin или manager."""

    role = serializers.ChoiceField(choices=[User.ROLE_ADMIN, User.ROLE_MANAGER])

    class Meta:
        model = User
        fields = ['role']

    def validate(self, attrs):
        request = self.context.get('request')
        instance = self.instance
        new_role = attrs.get('role')

        if not request or not getattr(request, "user", None) or not request.user.is_authenticated:
            raise serializers.ValidationError({'detail': 'Требуется авторизация.'})

        # Защита от потери доступа: нельзя менять роль самому себе.
        if instance and instance.pk == request.user.pk:
            raise serializers.ValidationError({'role': 'Нельзя менять роль самому себе.'})

        # Чтобы не "выключить" доступ всей системе: не меняем роль других админов.
        if instance and getattr(instance, "role", None) == User.ROLE_ADMIN:
            raise serializers.ValidationError({'role': 'Нельзя менять роль другого администратора.'})

        if new_role not in (User.ROLE_ADMIN, User.ROLE_MANAGER):
            raise serializers.ValidationError({'role': 'Можно назначить только администратора или менеджера.'})

        return attrs


class StaffUserPasswordSerializer(serializers.Serializer):
    """Смена пароля менеджера администратором."""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Пароли не совпадают'})
        try:
            validate_password(attrs['password'])
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        return attrs

    def save(self, **kwargs):
        user = self.context['user']
        user.set_password(self.validated_data['password'])
        user.save(update_fields=['password'])
        return user


class ProfilePasswordChangeSerializer(serializers.Serializer):
    """Смена пароля для текущего пользователя."""

    current_password = serializers.CharField(write_only=True, min_length=1)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not getattr(request, 'user', None) or not request.user.is_authenticated:
            raise serializers.ValidationError({'detail': 'Требуется авторизация.'})

        user = request.user

        if not user.check_password(attrs['current_password']):
            raise serializers.ValidationError({'current_password': 'Неверный текущий пароль'})

        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'Пароли не совпадают'})

        try:
            validate_password(attrs['new_password'], user)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})

        return attrs

    def save(self, **kwargs):
        request = self.context['request']
        user = request.user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user
