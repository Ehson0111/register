from django.contrib import admin

from .models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "invoice_number",
        "deal_id",
        "contact_name",
        "amount",
        "status",
        "onec_sync_status",
        "created_at",
    )
    search_fields = ("invoice_number", "contact_name", "contact_email", "onec_document_id")
    list_filter = ("status", "onec_sync_status", "crm_sync_status", "created_at")
