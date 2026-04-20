from django.db import models

# Create your models here.
# orders/models.py

from django.db import models

# apps/yookassa_integration/models.py

from django.db import models

class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        WAITING = 'waiting', 'Ожидает оплаты'
        PAID = 'paid', 'Оплачен'
        CANCELLED = 'cancelled', 'Отменён'
    
    invoice_number = models.CharField(max_length=50, unique=True)  # Номер счёта
    amount = models.DecimalField(max_digits=10, decimal_places=2)   # Сумма
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    payment_id = models.CharField(max_length=100, blank=True, null=True)  # ID из ЮKassa
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    
    # Для отправки в 1С
    sent_to_1c = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Счёт №{self.invoice_number} - {self.amount} руб."

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