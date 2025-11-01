# contacts/serializers.py

        
from rest_framework import serializers
from .models import Contact

class ContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact
        fields = 'first_name'


class ContactListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка контактов (меньше полей)"""
    class Meta:
        model = Contact
        fields = [
            'id', 'full_name', 'email', 'phone', 'company', 'position',
            'status', 'created_at'
        ]
        read_only_fields = ['created_at']

class ContactDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра и создания"""
    class Meta:
        model = Contact
        fields = [
            'id', 'full_name', 'email', 'phone', 'company', 'position',
            'tags', 'status', 'source', 'custom_fields', 'greeting',
            'owner_id', 'assigned_manager_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['owner_id', 'created_at', 'updated_at']