from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .models import Invoice
from .onec_client_v2 import OneCClientV2, OneCErrorV2


def create_invoice_in_onec(invoice, *, client=None): #создаёт счёт в 1С
    """
    Создание счета в 1С через новый  сервис
    """
    client = client or OneCClientV2() # Создаём клиент для 1С (если не передан)
    
    try:
        payload = client.create_invoice(invoice)  # Отправляем счёт в 1С
        # Сохраняем ID из 1С в CRM

        invoice.onec_document_id = payload.get("external_id_1c", "")
        invoice.onec_invoice_number = payload.get("invoice_number_1c") or invoice.invoice_number
        # Меняем статусы

        invoice.sent_to_1c = True  # Отправлен в 1С

        invoice.status = Invoice.Status.WAITING     # Ждёт оплаты

        invoice.onec_sync_status = Invoice.SyncStatus.SYNCED # Синхронизирован
        # Очищаем ошибки

        invoice.last_onec_error = ""
        invoice.next_retry_at = None  # Больше не ждём повтор
        
        invoice.save()   # Сохраняем в БД

        
        return invoice
    except OneCErrorV2 as e:
        invoice.mark_retry(error_text=str(e), onec=True) # Помечаем для повтора
        invoice.save()
        raise # Пробрасываем ошибку дальше (в views.py)
    


def register_payment_in_onec(invoice, payment_payload, *, client=None): #регистрирует оплату в 1С
    """
    Регистрация оплаты в 1С через новый   сервис
    """
    client = client or OneCClientV2()


    # Защита от дублей (идемпотентность):
    incoming_yk_id = (payment_payload.get("id") or "").strip()  # ID из вебхук
    stored_yk_id = (invoice.payment_id or "").strip()    # ID в CRM
    if invoice.status == Invoice.Status.PAID and invoice.onec_payment_document_id:
        if not incoming_yk_id:
            return invoice  # Нет ID  выходим
        if stored_yk_id and incoming_yk_id == stored_yk_id:
            return invoice # Та же оплата  выходим

    try:
        
        # Парсинг даты оплаты:

        captured_raw = payment_payload.get("captured_at") or ""
        parsed_captured = parse_datetime(captured_raw) if captured_raw else None
        if parsed_captured:
            invoice.paid_at = parsed_captured


        # Регистрация оплаты в 1С:

        payload = client.register_payment(invoice, payment_payload)
        invoice.onec_payment_document_id = payload.get("payment_document_id_1c", "") or invoice.onec_payment_document_id
        invoice.status = Invoice.Status.PAID # Оплачен
        invoice.crm_sync_status = Invoice.SyncStatus.SYNCED # Синхронизировано
        invoice.last_crm_error = ""
        if payload.get("invoice_status_updated") is True:     # Всё хорошо

            invoice.onec_sync_status = Invoice.SyncStatus.SYNCED
            invoice.last_onec_error = ""
            invoice.next_retry_at = None
        else:
            # Оплата создана и проведена, но статус счёта в 1С не обновился.
            # Сохраняем оплату в CRM и включаем ретраи только на обновление статуса счёта.
            invoice.mark_retry(
                error_text=payload.get("invoice_status_update_error") or "Статус счёта в 1С не обновился",
                onec=True,
            )
        if not invoice.paid_at:
            invoice.paid_at = timezone.now()
        invoice.save()
        return invoice
    except OneCErrorV2 as e:
        invoice.mark_retry(error_text=str(e), onec=True)
        invoice.save()
        raise

 
def retry_due_invoice_sync(invoice, *, client=None): # повторяет синхронизацию при ошибках
    """
    Повторная синхронизация счета с 1С
    """
    if invoice.onec_sync_status != Invoice.SyncStatus.ERROR:
        return invoice  # Нет ошибки  не нужно
    if invoice.next_retry_at and invoice.next_retry_at > timezone.now():
        return invoice  # Ещё не пришло время   ждём

    client = client or OneCClientV2()
    
    try:
        # Есть оплата (payment_id)


        if invoice.payment_id:
            
             #   : Счёт уже оплачен в CRM, но статус в 1С не обновился
            if invoice.status == Invoice.Status.PAID and invoice.onec_payment_document_id:
                #   Проверяем статус счёта в 1С     
                if client.is_invoice_paid_in_onec(invoice.onec_document_id):
                    # Уже оплачен просто обновляем статус в CRM

                    invoice.onec_sync_status = Invoice.SyncStatus.SYNCED
                    invoice.last_onec_error = ""
                    invoice.next_retry_at = None
                    invoice.save(update_fields=["onec_sync_status", "last_onec_error", "next_retry_at"])
                    return invoice
                # Пытаемся обновить статус счёта в 1С
                if not client.ensure_invoice_paid_status(invoice):
                    raise OneCErrorV2("Статус счёта в 1С не «Оплачен» после обновление")
                invoice.onec_sync_status = Invoice.SyncStatus.SYNCED
                invoice.last_onec_error = ""
                invoice.next_retry_at = None
                invoice.save(update_fields=["onec_sync_status", "last_onec_error", "next_retry_at"])
                return invoice
            payment_payload = {
                "id": invoice.payment_id,
                "status": "succeeded",
                "amount": {"value": str(invoice.amount), "currency": "RUB"},
                # "captured_at": invoice.paid_at.isoformat() if invoice.paid_at else None,
                "captured_at": invoice.paid_at.replace(microsecond=0).isoformat() if invoice.paid_at else None,
                "payment_method": {"type": "yookassa"},
            }
            return register_payment_in_onec(invoice, payment_payload, client=client)
        else:
            return create_invoice_in_onec(invoice, client=client)
    except OneCErrorV2 as e:
        raise
