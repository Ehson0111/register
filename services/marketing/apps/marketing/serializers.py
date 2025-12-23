from rest_framework import serializers
from .models import EmailCampaign, EmailTemplate, ContactSegment, CampaignStatistic

class EmailCampaignSerializer(serializers.ModelSerializer):
    """Сериализатор для email рассылок"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    campaign_type_display = serializers.CharField(source='get_campaign_type_display', read_only=True)
    open_rate = serializers.FloatField(read_only=True)
    click_rate = serializers.FloatField(read_only=True)
    progress = serializers.IntegerField(read_only=True)
    is_active_campaign = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = EmailCampaign
        fields = [
            'id',
            'name',
            'description',
            'campaign_type',
            'campaign_type_display',
            'subject',
            'body',
            'status',
            'status_display',
            'scheduled_for',
            'sent_at',
            'recipient_count',
            'sent_count',
            'opens_count',
            'clicks_count',
            'open_rate',
            'click_rate',
            'progress',
            'is_active_campaign',
            'created_by',
            'created_by_name',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'created_by', 'created_at', 'updated_at', 'sent_count',
            'opens_count', 'clicks_count', 'open_rate', 'click_rate', 'progress'
        ]


class EmailCampaignCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рассылки"""
    class Meta:
        model = EmailCampaign
        fields = [
            'name',
            'description',
            'campaign_type',
            'subject',
            'body',
            'body_html',
            'target_segment',
            'scheduled_for',
            'tags'
        ]
    
    def validate_target_segment(self, value):
        """Валидация сегмента получателей"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Сегмент должен быть JSON объектом")
        return value
    
    def create(self, validated_data):
        """Автоматически назначаем создателя"""
        request = self.context.get('request')
        validated_data['created_by'] = request.user
        validated_data['recipient_count'] = self.calculate_recipient_count(validated_data['target_segment'])
        return super().create(validated_data)
    
    def calculate_recipient_count(self, target_segment):
        """Рассчитываем количество получателей (пока заглушка)"""
        # В реальном проекте здесь будет запрос к contact-service
        return 1000


class EmailTemplateSerializer(serializers.ModelSerializer):
    """Сериализатор для шаблонов email"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = EmailTemplate
        fields = [
            'id',
            'name',
            'description',
            'category',
            'category_display',
            'subject',
            'body',
            'body_html',
            'variables',
            'used_count',
            'is_active',
            'created_by',
            'created_by_name',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'used_count']


class ContactSegmentSerializer(serializers.ModelSerializer):
    """Сериализатор для сегментов контактов"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ContactSegment
        fields = [
            'id',
            'name',
            'description',
            'filters',
            'contact_count',
            'last_calculated_at',
            'is_active',
            'created_by',
            'created_by_name',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'contact_count', 'last_calculated_at', 'created_at', 'updated_at']


class CampaignStatisticSerializer(serializers.ModelSerializer):
    """Сериализатор для статистики кампаний"""
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)
    open_rate = serializers.FloatField(read_only=True)
    click_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = CampaignStatistic
        fields = [
            'id',
            'campaign',
            'campaign_name',
            'date',
            'sent',
            'delivered',
            'opened',
            'clicked',
            'unsubscribed',
            'bounced',
            'complaints',
            'open_rate',
            'click_rate',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MarketingOverviewSerializer(serializers.Serializer):
    """Сериализатор для общей статистики маркетинга"""
    total_campaigns = serializers.IntegerField()
    active_campaigns = serializers.IntegerField()
    total_recipients = serializers.IntegerField()
    total_opens = serializers.IntegerField()
    total_clicks = serializers.IntegerField()
    average_open_rate = serializers.FloatField()
    average_click_rate = serializers.FloatField()
    template_count = serializers.IntegerField()
    segment_count = serializers.IntegerField()


class CampaignPerformanceSerializer(serializers.Serializer):
    """Сериализатор для производительности кампаний"""
    campaign_id = serializers.UUIDField()
    campaign_name = serializers.CharField()
    sent = serializers.IntegerField()
    opens = serializers.IntegerField()
    clicks = serializers.IntegerField()
    open_rate = serializers.FloatField()
    click_rate = serializers.FloatField()
    unsubscribes = serializers.IntegerField()
    revenue = serializers.FloatField()
    roi = serializers.FloatField()