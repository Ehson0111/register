 
from rest_framework import serializers
from django.utils import timezone
from .models import Template, Campaign

class TemplateSerializer(serializers.ModelSerializer):
    """Сериализатор для шаблонов"""
    template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)
    
    class Meta:
        model = Template
        fields = [
            'id', 'name', 'template_type', 'template_type_display',
            'subject', 'content', 'sms_content', 'variables',
            'description', 'manager_id', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'manager_id']
    
    def create(self, validated_data):
        """Автоматически добавляем manager_id"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['manager_id'] = request.user.id
        return super().create(validated_data)
    
    def validate(self, data):
        """Валидация в зависимости от типа шаблона"""
        template_type = data.get('template_type', self.instance.template_type if self.instance else 'email')
        
        if template_type == 'email' and not data.get('subject'):
            raise serializers.ValidationError({
                "subject": "Для email шаблона требуется тема"
            })
        
        if template_type == 'sms' and not data.get('sms_content'):
            raise serializers.ValidationError({
                "sms_content": "Для SMS шаблона требуется текст"
            })
        
        return data

class CampaignSerializer(serializers.ModelSerializer):
    """Список рассылок на экране маркетинга (без тяжёлого recipients_detail)."""

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    campaign_type_display = serializers.CharField(source='get_campaign_type_display', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    delivery_rate = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'campaign_type', 'campaign_type_display',
            'status', 'status_display', 'template', 'template_name',
            'subject', 'content', 'recipients', 'recipient_count',
            'success_count', 'failed_count', 'sent_at',
            'delivery_rate',
            'manager_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'manager_id']
    
    def get_delivery_rate(self, obj):
        """Процент успешной доставки"""
        if obj.recipient_count > 0:
            return round((obj.success_count / obj.recipient_count) * 100, 2)
        return 0
    
    def create(self, validated_data):
        """Создание кампании с автоматическим manager_id"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['manager_id'] = request.user.id
        
        # Устанавливаем количество получателей
        recipients = validated_data.get('recipients', [])
        validated_data['recipient_count'] = len(recipients)
        
        return super().create(validated_data)

class SendCampaignSerializer(serializers.Serializer):
    """Сериализатор для отправки кампании с шаблоном"""
    template_id = serializers.IntegerField(required=True)
    subject = serializers.CharField(required=False, allow_blank=True)
    content = serializers.CharField(required=False, allow_blank=True)
    
    # Переменные для подстановки в шаблон
    variables = serializers.JSONField(
        required=False, 
        default=dict,
        help_text="Переменные для подстановки в шаблон"
    )
    
    # Выбор получателей
    recipient_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text="Список ID получателей"
    )
    
    # Или можно отправить всем клиентам
    send_to_all = serializers.BooleanField(default=False, required=False)
    
    campaign_name = serializers.CharField(
        required=False, 
        default="Новая рассылка",
        help_text="Название кампании (если не указано, будет сгенерировано автоматически)"
    )
    
    def validate(self, data):
        """Валидация данных"""
        if not data.get('recipient_ids') and not data.get('send_to_all'):
            raise serializers.ValidationError({
                "recipient_ids": "Необходимо указать получателей или выбрать 'send_to_all'"
            })
        
        return data


class QuickMessageSerializer(serializers.Serializer):
    """Сериализатор для быстрой отправки сообщения без шаблона"""
    message = serializers.CharField(required=True, help_text="Текст сообщения")
    subject = serializers.CharField(required=False, allow_blank=True, help_text="Тема сообщения")
    
    recipient_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text="Список ID получателей"
    )
    
    # Можно указать тип сообщения
    message_type = serializers.ChoiceField(
        choices=[('email', 'Email'), ('sms', 'SMS')],
        default='email',
        required=False
    )
    
    campaign_name = serializers.CharField(
        required=False, 
        default="Быстрая рассылка",
        help_text="Название кампании"
    )