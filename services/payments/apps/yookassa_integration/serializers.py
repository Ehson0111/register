from rest_framework import serializers

from .models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "id",
            "deal_id",
            "deal_title",
            "contact_id",
            "contact_name",
            "contact_email",
            "contact_phone",
            "service_id",
            "service_name",
            "comment",
            "invoice_number",
            "onec_document_id",
            "onec_invoice_number",
            "onec_payment_document_id",
            "amount",
            "status",
            "payment_id",
            "payment_url",
            "onec_sync_status",
            "crm_sync_status",
            "onec_retry_count",
            "crm_retry_count",
            "last_onec_error",
            "last_crm_error",
            "created_at",
            "paid_at",
            "sent_to_1c",
            "pay_link_sent_at",
            "next_retry_at",
        ]
        read_only_fields = fields
