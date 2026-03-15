from django.contrib import admin
from .models import Applications

@admin.register(Applications)
class ApplicationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'subject', 'sender_email', 'is_processed', 'created_at')
    list_filter = ('is_processed', 'sender_email')
    search_fields = ('subject', 'text', 'sender_email', 'message_id')
    ordering = ('-date',)
