# from django.urls import path
# from . import views

# app_name = 'yookassa_integration'

# urlpatterns = [
#     path('create-test-payment/', views.test_payment, name='create_test_payment'),
#     path('webhook/', views.yookassa_webhook, name='yookassa_webhook'),
#     path('success/', views.payment_success, name='payment_success'),
# ]


# apps/yookassa_integration/urls.py

from django.urls import path
from . import views

app_name = 'yookassa_integration'

urlpatterns = [
    # Оплатить счёт (клиент переходит по этой ссылке)
    path('pay/<int:invoice_id>/', views.create_invoice_and_pay, name='pay_invoice'),
    
    # Результат оплаты
    path('result/<int:invoice_id>/', views.payment_result, name='payment_result'),
    
    # Webhook от ЮKassa
    path('webhook/', views.yookassa_webhook, name='yookassa_webhook'),
]