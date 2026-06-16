
import re

from rest_framework import serializers
from .models import Contact, Service, Deal, DealStage, AuditTrail, ContactCompanyDetails

PHONE_RE = re.compile(r"^[\d\s+\-()]{7,20}$")
INN_RE = re.compile(r"^\d{10}$|^\d{12}$")


class ContactCompanyDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactCompanyDetails
        fields = [
            'company_name',
            'inn',
            'kpp',
            'ogrn',
            'status_text',
            'address',
            'okved',
            'director',
            'updated_at',
        ]

class ContactListSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для списка контактов"""
    full_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    active_deals_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Contact
        fields = [
            'id',
            'full_name',
            'position',
            "first_name",
            "last_name",
            'email',
            'phone',
            'inn',
            
            'address',
            'notes',
            'company',
            'status',
            'status_display',
            'active_deals_count',
            'created_at'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_active_deals_count(self, obj):
        return obj.deals.exclude(status__in=[Deal.DEAL_WON, Deal.DEAL_LOST]).count()

class ContactDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра и редактирования"""
    full_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    deals = serializers.SerializerMethodField()
    company_details = ContactCompanyDetailsSerializer(read_only=True)
    
    class Meta:
        model = Contact
        fields = [
            'id',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'phone',
            'inn',
            'status',
            
            'status_display',
            'company',
            'position',
            'address',
            'notes',
            'company_details',
            'deals',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'full_name', 'status_display', 'deals']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_deals(self, obj):
        deals = obj.deals.all()[:10]  # Ограничиваем количество для превью
        return DealListSerializer(deals, many=True).data
    
    def validate_email(self, value):
        """Валидация уникальности email"""
        if Contact.objects.filter(email=value).exists():
            if self.instance and self.instance.email == value:
                return value
            raise serializers.ValidationError("Контакт с таким email уже существует")
        return value

class AddContactSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления нового контакта"""
    
    class Meta:
        model = Contact
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'inn',
            'status',
            'company',
            'position',
            'address',
            'notes'
        ]
    
    def validate_first_name(self, value):
        value = (value or "").strip()
        if len(value) < 2:
            raise serializers.ValidationError("Имя должно содержать минимум 2 символа")
        return value

    def validate_last_name(self, value):
        value = (value or "").strip()
        if len(value) < 2:
            raise serializers.ValidationError("Фамилия должна содержать минимум 2 символа")
        return value

    def validate_email(self, value):
        """Валидация email и уникальности при создании"""
        value = (value or "").strip().lower()
        if Contact.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Контакт с таким email уже существует")
        return value

    def validate_phone(self, value):
        value = (value or "").strip()
        if not value:
            return value
        if not PHONE_RE.match(value):
            raise serializers.ValidationError("Некорректный формат телефона")
        return value

    def validate_inn(self, value):
        value = (value or "").strip()
        if not value:
            return value
        if not INN_RE.match(value):
            raise serializers.ValidationError("ИНН должен содержать 10 или 12 цифр")
        return value

    def validate_status(self, value):
        valid = {choice[0] for choice in Contact.STATUS_CHOICES}
        if value not in valid:
            raise serializers.ValidationError("Недопустимый статус контакта")
        return value

    def create(self, validated_data):
        """Создание контакта"""
        return Contact.objects.create(**validated_data)

# Новые сериализаторы для услуг и сделок
class ServiceSerializer(serializers.ModelSerializer):
    """Сериализатор для услуг"""
    active_deals_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = [
            'id',
            'name',
            'description',
            'price',
            'duration_days',
            'is_active',
            'active_deals_count',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'active_deals_count']
    
    def get_active_deals_count(self, obj):
        return obj.deals.exclude(status__in=[Deal.DEAL_WON, Deal.DEAL_LOST]).count()


class DealStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DealStage
        fields = ["id", "name", "order", "color", "is_default"]


class DealListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка сделок"""
    contact_name = serializers.CharField(source='contact.get_full_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    # service_Id = serializers.CharField(source='service.id' )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_color = serializers.SerializerMethodField()
    is_closed = serializers.BooleanField(read_only=True)
    stage_name = serializers.CharField(source="stage.name", read_only=True)
    stage_color = serializers.CharField(source="stage.color", read_only=True)
    # contactId=serializers.CharField(source='contact.id')
    
    class Meta:
        model = Deal
        fields = [
            'id',
            'title',
            'contact_name',
            # "contactId",
            'description',
            'contact',
            'service',
            


            'service_name',
            'amount',
            'status',
            'status_display',
            'status_color',
            'is_closed',
            "stage",
            "stage_name",
            "stage_color",
            'expected_close_date',
            'created_at'
        ]
    
    def get_status_color(self, obj):
        return obj.get_status_color()

class DealDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра сделки"""
    contact_name = serializers.CharField(source='contact.get_full_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_color = serializers.SerializerMethodField()
    is_closed = serializers.BooleanField(read_only=True)
    stage_name = serializers.CharField(source="stage.name", read_only=True)
    stage_color = serializers.CharField(source="stage.color", read_only=True)
    
    days_open = serializers.SerializerMethodField()
    
    class Meta:
        model = Deal
        fields = [
            'id',
            'title',
            'description',
             
            'contact',
            'contact_name',
            'service',
            'service_name',
            'amount',
            'status',
            'status_display',
            'status_color',
            'is_closed',
            "stage",
            "stage_name",
            "stage_color",
            'expected_close_date',
            'actual_close_date',
            'days_open',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_closed', 'days_open']
    
    def get_status_color(self, obj):
        return obj.get_status_color()
    
    def get_days_open(self, obj):
        from django.utils import timezone
        return (timezone.now().date() - obj.created_at.date()).days

class CreateDealSerializer(serializers.ModelSerializer):
    """Сериализатор для создания сделки"""
    
    class Meta:
        model = Deal
        fields = [
            'title',
            'description',
            'contact',
            'service',
            'amount',
            'status',
            "stage",
            'expected_close_date'
        ]
    
    def validate(self, data):
        """Дополнительная валидация"""
        if data.get('amount') <= 0:
            raise serializers.ValidationError({
                "amount": "Сумма сделки должна быть больше 0"
            })
        
        return data

    def create(self, validated_data):
        if not validated_data.get("stage"):
            default_stage = DealStage.objects.filter(is_default=True).order_by("order", "id").first()
            validated_data["stage"] = default_stage or DealStage.objects.order_by("order", "id").first()
        return super().create(validated_data)
    





class SimpleServiceSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для услуг (только для выбора)"""
    class Meta:
        model = Service
        fields = ['id', 'name', 'price']

class SimpleContactSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для контактов (только для выбора)"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Contact
        fields = ['id', 'full_name', 'company']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class AuditTrailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditTrail
        fields = [
            "id",
            "actor",
            "action",
            "entity_type",
            "entity_id",
            "metadata",
            "created_at",
        ]
        
