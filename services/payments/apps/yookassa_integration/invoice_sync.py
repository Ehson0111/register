from django.utils import timezone

from .models import Invoice
from .onec_client import OneCClient


def create_invoice_in_onec(invoice, *, client=None):
    client = client or OneCClient()
    payload = client.create_invoice_document(invoice)
    invoice.onec_document_id = payload.get("external_id_1c", "")
    invoice.onec_invoice_number = payload.get("invoice_number_1c") or invoice.invoice_number
    invoice.sent_to_1c = True
    invoice.status = Invoice.Status.WAITING
    invoice.onec_sync_status = Invoice.SyncStatus.SYNCED
    invoice.last_onec_error = ""
    invoice.next_retry_at = None
    invoice.save()
    return invoice


def register_payment_in_onec(invoice, payment_payload, *, client=None):
    client = client or OneCClient()
    payload = client.register_payment(invoice, payment_payload)
    invoice.onec_payment_document_id = payload.get("payment_document_id_1c", "")
    invoice.status = Invoice.Status.PAID
    invoice.onec_sync_status = Invoice.SyncStatus.SYNCED
    invoice.crm_sync_status = Invoice.SyncStatus.SYNCED
    invoice.last_onec_error = ""
    invoice.last_crm_error = ""
    invoice.next_retry_at = None
    if not invoice.paid_at:
        invoice.paid_at = timezone.now()
    invoice.save()
    return invoice


def retry_due_invoice_sync(invoice, *, client=None):
    if invoice.onec_sync_status != Invoice.SyncStatus.ERROR:
        return invoice
    if invoice.next_retry_at and invoice.next_retry_at > timezone.now():
        return invoice

    client = client or OneCClient()
    if invoice.payment_id:
        payment_payload = {
            "id": invoice.payment_id,
            "status": "succeeded",
            "amount": {"value": str(invoice.amount), "currency": "RUB"},
            "captured_at": invoice.paid_at.isoformat() if invoice.paid_at else None,
            "payment_method": {"type": "yookassa"},
        }
        return register_payment_in_onec(invoice, payment_payload, client=client)
    return create_invoice_in_onec(invoice, client=client)
