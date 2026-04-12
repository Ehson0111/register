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


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Публичная регистрация: всегда создаётся клиент (роль нельзя выбрать из API)."""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password_confirm']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Пароли не совпадают"})
        try:
            validate_password(attrs['password'])
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        user.role = User.ROLE_CLIENT
        user.save(update_fields=['role'])
        UserProfile.objects.get_or_create(user=user)
        return user


class UserListSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'role', 'role_display', 'is_active', 'date_joined',
        ]


class StaffCreateUserSerializer(serializers.ModelSerializer):
    """Создание пользователя: менеджер — только клиент; администратор — менеджер или клиент."""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
        choices=[User.ROLE_MANAGER, User.ROLE_CLIENT],
        help_text='Менеджер через API может выбрать только client.',
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

        request = self.context.get('request')
        actor = getattr(request, 'user', None) if request else None
        actor_role = getattr(actor, 'role', None) if actor and actor.is_authenticated else None
        role = attrs.get('role')

        if actor_role == User.ROLE_MANAGER:
            if role != User.ROLE_CLIENT:
                raise serializers.ValidationError(
                    {'role': 'Менеджер может создавать только клиентов. Менеджеров добавляет администратор.'}
                )
        elif actor_role == User.ROLE_ADMIN:
            if role not in (User.ROLE_MANAGER, User.ROLE_CLIENT):
                raise serializers.ValidationError({'role': 'Недопустимая роль.'})
        else:
            raise serializers.ValidationError({'role': 'Нет прав для создания пользователя.'})

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