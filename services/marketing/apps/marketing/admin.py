from django.contrib import admin

# Register your models here.
# services/marketing/apps/marketing/admin.py
from django.contrib import admin
from .models import Template, Campaign, CampaignRecipient

@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'manager_id', 'is_active', 'created_at')
    list_filter = ('template_type', 'is_active', 'created_at')
    search_fields = ('name', 'subject', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'template_type', 'description', 'manager_id', 'is_active')
        }),
        ('Содержимое', {
            'fields': ('subject', 'content', 'sms_content', 'variables')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'campaign_type', 'status', 'manager_id', 
                    'recipient_count', 'sent_at', 'created_at')
    list_filter = ('campaign_type', 'status', 'sent_at', 'created_at')
    search_fields = ('name', 'subject', 'content')
    readonly_fields = ('created_at', 'updated_at', 'success_count', 
                      'failed_count', 'recipient_count')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'campaign_type', 'status', 'manager_id')
        }),
        ('Шаблон и содержимое', {
            'fields': ('template', 'subject', 'content')
        }),
        ('Получатели', {
            'fields': ('recipients', 'recipient_count')
        }),
        ('Статистика', {
            'fields': ('success_count', 'failed_count', 'sent_at'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CampaignRecipient)
class CampaignRecipientAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'recipient_id', 'status', 'sent_at', 
                    'delivered_at', 'opened_at')
    list_filter = ('status', 'sent_at', 'created_at')
    search_fields = ('recipient_email', 'recipient_phone', 'error_message')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('campaign', 'recipient_id', 'status')
        }),
        ('Контактные данные', {
            'fields': ('recipient_email', 'recipient_phone')
        }),
        ('Статусы отправки', {
            'fields': ('sent_at', 'delivered_at', 'opened_at', 'error_message')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )