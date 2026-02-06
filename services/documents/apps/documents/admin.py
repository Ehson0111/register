from django.contrib import admin
from .models import ClientDocument

@admin.register(ClientDocument)
class ClientDocumentAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'client_id', 'uploaded_by', 'uploaded_at', 'file_size')
    search_fields = ('original_filename', 'client_id')
    list_filter = ('uploaded_at',)