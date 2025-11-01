# contacts/serializers.py

        
from rest_framework import serializers
from .models import Contact

# class ContactSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Contact
#         fields = 'first_name'


# class ContactListSerializer(serializers.ModelSerializer):
#     """Сериализатор для списка контактов (меньше полей)"""
#     class Meta:
#         model = Contact
#         fields = [
#             'id', 'full_name', 'email', 'phone', 'company', 'position',
#             'status', 'created_at'
#         ]
#         read_only_fields = ['created_at']

# class ContactDetailSerializer(serializers.ModelSerializer):
#     """Сериализатор для детального просмотра и создания"""
#     class Meta:
#         model = Contact
#         fields = [
#             'id', 'full_name', 'email', 'phone', 'company', 'position',
#             'tags', 'status', 'source', 'custom_fields', 'greeting',
#             'owner_id', 'assigned_manager_id',
#             'created_at', 'updated_at'
#         ]
#         read_only_fields = ['owner_id', 'created_at', 'updated_at']

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
    
# class Contact(models.Model):
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     email = models.EmailField("Email")
#     phone = models.CharField( max_length=20, blank=True)
#     # owner = models.ForeignKey(
#     #     User, 
#     #     on_delete=models.CASCADE, 
#     #     verbose_name="Владелец",
#     #     related_name="contacts"
#     # )
#     # created_at = models.DateTimeField("auto_now_add=True)
#     # updated_at = models.DateTimeField("Обновлено", auto_now=True)

#     class Meta:
#     #     verbose_name = "Контакт"
#     #     verbose_name_plural = "Контакты"
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"{self.first_name}"