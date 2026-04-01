# # contacts/admin.py

# from django.contrib import admin
# from .models import Contact

# @admin.register(Contact)
# class ContactAdmin(admin.ModelAdmin):
#     list_display = ('first_name', 'last_name', 'email', 'phone')
#     search_fields = ('first_name', 'last_name', 'email')
from django.contrib import admin
from django.utils.html import format_html
from .models import Contact, Service, Deal, AuditTrail

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = [
        'get_full_name', 
        'email', 
        'phone', 
        'company', 
        'status', 
        'created_at',
        'active_deals_count'
    ]
    list_filter = ['status', 'company', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'company', 'phone']
    readonly_fields = ['created_at', 'active_deals_count']
    fieldsets = [
        ('Основная информация', {
            'fields': [
                'first_name', 
                'last_name', 
                'email', 
                'phone'
            ]
        }),
        ('Работа', {
            'fields': [
                'company', 
                'position'
            ]
        }),
        ('Статус и заметки', {
            'fields': [
                'status',
                'address', 
                'notes'
            ]
        }),
        ('Системная информация', {
            'fields': [
                'created_at',
                'active_deals_count'
            ],
            'classes': ['collapse']
        }),
    ]
    
    def active_deals_count(self, obj):
        return obj.deals.exclude(status__in=[Deal.DEAL_WON, Deal.DEAL_LOST]).count()
    active_deals_count.short_description = 'Активные сделки'

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'price', 
        'duration_days', 
        'is_active', 
        'created_at',
        'active_deals_count'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_active']
    readonly_fields = ['created_at', 'active_deals_count']
    fieldsets = [
        ('Основная информация', {
            'fields': [
                'name',
                'description'
            ]
        }),
        ('Цена и сроки', {
            'fields': [
                'price',
                'duration_days'
            ]
        }),
        ('Статус', {
            'fields': [
                'is_active'
            ]
        }),
        ('Системная информация', {
            'fields': [
                'created_at',
                'active_deals_count'
            ],
            'classes': ['collapse']
        }),
    ]
    
    def active_deals_count(self, obj):
        return obj.deals.exclude(status__in=[Deal.DEAL_WON, Deal.DEAL_LOST]).count()
    active_deals_count.short_description = 'Активные сделки'

@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'contact',
        'service',
        'amount',
        'probability',
        'status_colored',
        'expected_close_date',
        'created_at',
        'is_closed'
    ]
    list_filter = [
        'status', 
        'service',
        'created_at',
        'expected_close_date'
    ]
    search_fields = [
        'title', 
        'description',
        'contact__first_name',
        'contact__last_name',
        'contact__company'
    ]
    readonly_fields = [
        'created_at', 
        'updated_at', 
        'is_closed',
        'days_open_display'
    ]
    autocomplete_fields = ['contact', 'service']
    date_hierarchy = 'created_at'
    
    fieldsets = [
        ('Основная информация', {
            'fields': [
                'title',
                'contact',
                'service'
            ]
        }),
        ('Детали сделки', {
            'fields': [
                'description',
                'amount',
                'probability'
            ]
        }),
        ('Статус и даты', {
            'fields': [
                'status',
                'expected_close_date',
                'actual_close_date'
            ]
        }),
        ('Системная информация', {
            'fields': [
                'is_closed',
                'days_open_display',
                'created_at',
                'updated_at'
            ],
            'classes': ['collapse']
        }),
    ]
    
    def status_colored(self, obj):
        color_map = {
            Deal.DEAL_NEW: 'blue',
            Deal.DEAL_IN_PROGRESS: 'orange',
            Deal.DEAL_WON: 'green',
            Deal.DEAL_LOST: 'red',
            Deal.DEAL_ON_HOLD: 'gray',
        }
        color = color_map.get(obj.status, 'blue')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = 'Статус'
    
    def days_open_display(self, obj):
        from django.utils import timezone
        days = (timezone.now().date() - obj.created_at.date()).days
        return f"{days} дней"
    days_open_display.short_description = 'Дней в работе'
    
    def is_closed(self, obj):
        return obj.is_closed()
    is_closed.boolean = True
    is_closed.short_description = 'Закрыта'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('contact', 'service')

    def save_model(self, request, obj, form, change):
        """Автоматическое обновление даты закрытия при выигрыше/проигрыше сделки"""
        if obj.status in [Deal.DEAL_WON, Deal.DEAL_LOST] and not obj.actual_close_date:
            from django.utils import timezone
            obj.actual_close_date = timezone.now().date()
        super().save_model(request, obj, form, change)





# @admin.register(Contact)
# class ContactAdmin(admin.ModelAdmin):
#     list_display = ['get_full_name', 'email', 'company', 'status', 'created_at']
#     search_fields = ['first_name', 'last_name', 'email', 'company']
#     list_filter = ['status', 'created_at']

# @admin.register(Service)
# class ServiceAdmin(admin.ModelAdmin):
#     list_display = ['name', 'price', 'duration_days', 'is_active']
#     list_filter = ['is_active', 'created_at']
#     search_fields = ['name']

# @admin.register(Deal)
# class DealAdmin(admin.ModelAdmin):
#     list_display = ['title', 'contact', 'service', 'amount', 'status', 'created_at']
#     list_filter = ['status', 'service', 'created_at']
#     search_fields = ['title', 'contact__first_name', 'contact__last_name']
#     autocomplete_fields = ['contact', 'service']


@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ["created_at", "actor", "action", "entity_type", "entity_id"]
    list_filter = ["action", "entity_type", "created_at"]
    search_fields = ["actor", "action", "entity_type"]
    readonly_fields = ["created_at", "actor", "action", "entity_type", "entity_id", "metadata"]