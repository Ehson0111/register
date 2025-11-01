from rest_framework import serializers
from .models import Contact

class ContactListSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для списка контактов"""
    full_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Contact
        fields = [
            'id',
            'full_name',
            'email',
            'phone',
            'company',
            'status',
            'status_display',
            'created_at'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()

class ContactDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра и редактирования"""
    full_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Contact
        fields = [
            'id',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'phone',
            'status',
            'status_display',
            'company',
            'position',
            'address',
            'notes',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'full_name', 'status_display']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def validate_email(self, value):
        """Валидация уникальности email"""
        if Contact.objects.filter(email=value).exists():
            if self.instance and self.instance.email == value:
                return value
            raise serializers.ValidationError("Контакт с таким email уже существует")
        return value

class AddContactSerializer(serializers.ModelSerializer):  # Исправил - убрал скобки
    """Сериализатор для добавления нового контакта"""
    
    class Meta:
        model = Contact
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'status',
            'company',
            'position',
            'address',
            'notes'
        ]
    
    def validate_email(self, value):
        """Валидация уникальности email при создании"""
        if Contact.objects.filter(email=value).exists():
            raise serializers.ValidationError("Контакт с таким email уже существует")
        return value
    
    def create(self, validated_data):
        """Создание контакта"""
        return Contact.objects.create(**validated_data)