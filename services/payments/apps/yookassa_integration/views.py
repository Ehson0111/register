
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from yookassa import Configuration, Payment
from django.conf import settings
import json
import uuid
from .models import Invoice

# Настройка ЮKassa
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from yookassa import Configuration, Payment
from django.conf import settings
import json
import uuid

# Настройка ЮKassa
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

def test_payment(request):
    """Создаёт тестовый платёж и возвращает ссылку на оплату"""
    idempotence_key = str(uuid.uuid4())
    
    payment = Payment.create({
        "amount": {
            "value": "100.00",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://1d6d-84-201-6-10.ngrok-free.app/payment/success/"
        },
        "capture": True,
        "description": "Тестовый платёж для диплома"
    }, idempotence_key)
    
    return JsonResponse({
        'payment_id': payment.id,
        'status': payment.status,
        'confirmation_url': payment.confirmation.confirmation_url
    })

@csrf_exempt
@require_http_methods(['POST'])
def yookassa_webhook(request):
    """Обработчик уведомлений от ЮKassa"""
    try:
        event_json = json.loads(request.body)
        print(f"📩 Получено уведомление: {event_json}")
        
        # Здесь будет логика смены статуса заказа
        # Пока просто отвечаем, что всё ок
        
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return JsonResponse({'error': str(e)}, status=400)

def payment_success(request):
    """Страница успешной оплаты"""
    return HttpResponse("""
        <h1>✅ Оплата прошла успешно!</h1>
        <p>Спасибо за покупку. Ваш заказ принят в обработку.</p>
        <a href="/">Вернуться на главную</a>
    """)
    
# apps/yookassa_integration/views.py

def create_invoice_and_pay(request, invoice_id):
    """
    Шаг 1: Находим счёт
    Шаг 2: Создаём платёж в ЮKassa
    Шаг 3: Отправляем пользователя на оплату
    """
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Создаём платёж в ЮKassa
    idempotence_key = str(uuid.uuid4())
    
    payment = Payment.create({
        "amount": {
            "value": str(invoice.amount),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": f"https://c16e-84-200-73-85.ngrok-free.app/payment/result/{invoice.id}/"
        },
        "capture": True,
        "description": f"Оплата счёта №{invoice.invoice_number}",
        "metadata": {
            "invoice_id": str(invoice.id),
            "invoice_number": invoice.invoice_number
        }
    }, idempotence_key)
    
    # Сохраняем payment_id в счёте
    invoice.payment_id = payment.id
    invoice.status = Invoice.Status.WAITING
    invoice.save()
    
    # Отправляем пользователя на страницу оплаты
    return redirect(payment.confirmation.confirmation_url)

def payment_result(request, invoice_id):
    """Страница после оплаты"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if invoice.status == Invoice.Status.PAID:
        return HttpResponse(f"""
            <h1>✅ Оплата прошла успешно!</h1>
            <p>Счёт №{invoice.invoice_number} на сумму {invoice.amount} руб. оплачен.</p>
            <p>Статус обновлён в 1С.</p>
            <a href="/">Вернуться на главную</a>
        """)
    else:
        return HttpResponse(f"""
            <h1>⏳ Оплата ещё не подтверждена</h1>
            <p>Счёт №{invoice.invoice_number} ожидает оплаты.</p>
            <p>Обновите страницу через несколько секунд.</p>
        """)

@csrf_exempt
@require_http_methods(['POST'])
def yookassa_webhook(request):
    """
    ВАЖНО: СЮДА ЮKASSA ПРИШЛЁТ УВЕДОМЛЕНИЕ ПОСЛЕ ОПЛАТЫ
    Здесь мы меняем статус и отправляем в 1С
    """
    try:
        event_json = json.loads(request.body)
        print(f"📩 Получено уведомление: {event_json}")
        
        # Проверяем, что это уведомление об успешной оплате
        if event_json.get('event') == 'payment.succeeded':
            payment = event_json['object']
            payment_id = payment['id']
            metadata = payment.get('metadata', {})
            invoice_id = metadata.get('invoice_id')
            
            if invoice_id:
                # Находим счёт
                invoice = Invoice.objects.get(id=invoice_id)
                
                # Меняем статус
                invoice.status = Invoice.Status.PAID
                invoice.paid_at = payment.get('paid_at')
                invoice.save()
                
                print(f"✅ Счёт №{invoice.invoice_number} оплачен!")
                
                # 🔥 ОТПРАВЛЯЕМ В 1С 🔥
                send_to_1c(invoice)
                
                return JsonResponse({'status': 'ok'})
        
        return JsonResponse({'status': 'ignored'})
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return JsonResponse({'error': str(e)}, status=400)

def send_to_1c(invoice):
    """
    Отправка обновлённого статуса в 1С
    """
    import requests
    
    # Твой URL для 1С (замени на реальный)
    one_c_url = "https://твой-сервер-1с.ru/api/invoice/update"
    
    data = {
        "invoice_number": invoice.invoice_number,
        "status": "paid",
        "amount": str(invoice.amount),
        "paid_at": invoice.paid_at.isoformat() if invoice.paid_at else None
    }
    
    try:
        response = requests.post(one_c_url, json=data, timeout=10)
        invoice.sent_to_1c = response.status_code == 200
        invoice.save()
        print(f"📤 Отправка в 1С: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Ошибка отправки в 1С: {e}")