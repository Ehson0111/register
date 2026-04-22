from datetime import timedelta

from django.db import models
from django.utils import timezone

class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        WAITING = 'waiting', 'Ожидает оплаты'
        PAID = 'paid', 'Оплачен'
        CANCELLED = 'cancelled', 'Отменён'

    class SyncStatus(models.TextChoices):
        PENDING = 'pending', 'Ожидает синхронизации'
        SYNCED = 'synced', 'Синхронизирован'
        ERROR = 'error', 'Ошибка синхронизации'

    deal_id = models.PositiveIntegerField(unique=True)
    deal_title = models.CharField(max_length=255, blank=True)
    contact_id = models.PositiveIntegerField(blank=True, null=True)
    contact_name = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=32, blank=True)
    service_id = models.PositiveIntegerField(blank=True, null=True)
    service_name = models.CharField(max_length=255, blank=True)
    comment = models.TextField(blank=True)
    invoice_number = models.CharField(max_length=50, unique=True)
    onec_document_id = models.CharField(max_length=128, blank=True)
    onec_invoice_number = models.CharField(max_length=128, blank=True)
    onec_payment_document_id = models.CharField(max_length=128, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_url = models.URLField(blank=True)
    onec_sync_status = models.CharField(max_length=20, choices=SyncStatus.choices, default=SyncStatus.PENDING)
    crm_sync_status = models.CharField(max_length=20, choices=SyncStatus.choices, default=SyncStatus.PENDING)
    onec_retry_count = models.PositiveIntegerField(default=0)
    crm_retry_count = models.PositiveIntegerField(default=0)
    last_onec_error = models.TextField(blank=True)
    last_crm_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    sent_to_1c = models.BooleanField(default=False)
    pay_link_sent_at = models.DateTimeField(blank=True, null=True)
    next_retry_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Счёт №{self.invoice_number} - {self.amount} руб."

    def mark_retry(self, *, error_text="", onec=False, crm=False):
        if onec:
            self.onec_sync_status = self.SyncStatus.ERROR
            self.onec_retry_count += 1
            self.last_onec_error = error_text
        if crm:
            self.crm_sync_status = self.SyncStatus.ERROR
            self.crm_retry_count += 1
            self.last_crm_error = error_text
        backoff_minutes = min(max(self.onec_retry_count + self.crm_retry_count, 1) * 5, 60)
        self.next_retry_at = timezone.now() + timedelta(minutes=backoff_minutes)

class Order(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Ожидает оплаты'
        PAID = 'paid', 'Оплачен'
        FAILED = 'failed', 'Ошибка'
        REFUNDED = 'refunded', 'Возврат'
    
    # ... твои существующие поля (номер заказа, сумма, клиент и т.д.)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name='Статус оплаты'
    )
    payment_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='ID платежа в ЮKassa'
    )
    
    def __str__(self):
        return f'Заказ №{self.id}'