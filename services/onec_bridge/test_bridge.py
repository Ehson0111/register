#!/usr/bin/env python3
"""
Тестовый скрипт для проверки bridge сервиса
"""
import requests
import json
import sys

BRIDGE_URL = "http://127.0.0.1:8013"
BRIDGE_SECRET = ""  # Установите ваш секретный ключ

def test_health():
    """Проверка health endpoint"""
    print("=== Тест Health Check ===")
    try:
        response = requests.get(f"{BRIDGE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_create_invoice():
    """Тест создания счета"""
    print("\n=== Тест Создания Счета ===")
    payload = {
        "crm_invoice_id": "12345",
        "crm_deal_id": "67890",
        "customer_name": "Иванов Иван Иванович",
        "customer_email": "ivanov@example.com",
        "service_name": "Консультационная услуга",
        "amount": "15000.00",
        "comment": "Тестовый счет для проверки интеграции"
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Bridge-Secret": BRIDGE_SECRET
    }
    
    try:
        response = requests.post(f"{BRIDGE_URL}/invoice/create", 
                               json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_register_payment():
    """Тест регистрации оплаты"""
    print("\n=== Тест Регистрации Оплаты ===")
    payload = {
        "crm_invoice_id": "12345",
        "onec_document_id": "00000000-0000-0000-0000-000000000001",
        "yookassa_payment_id": "yp_1234567890",
        "amount": "15000.00",
        "payment_date": "2026-04-22T23:30:00",
        "payment_method": "yookassa",
        "comment": "Оплата через YooKassa"
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Bridge-Secret": BRIDGE_SECRET
    }
    
    try:
        response = requests.post(f"{BRIDGE_URL}/payment/register", 
                               json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_legacy_invoke():
    """Тест legacy совместимости"""
    print("\n=== Тест Legacy Invoke ===")
    payload = {
        "method": "GET",
        "path": "$metadata",
        "params": {},
        "timeout": 20,
        "restart_before_request": False
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Bridge-Secret": BRIDGE_SECRET
    }
    
    try:
        response = requests.post(f"{BRIDGE_URL}/invoke", 
                               json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("Начало тестирования Bridge сервиса...")
    print(f"URL: {BRIDGE_URL}")
    
    tests = [
        ("Health Check", test_health),
        ("Create Invoice", test_create_invoice),
        ("Register Payment", test_register_payment),
        ("Legacy Invoke", test_legacy_invoke)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        result = test_func()
        results.append((test_name, result))
        print(f"Result: {'✅ PASS' if result else '❌ FAIL'}")
    
    print(f"\n{'='*50}")
    print("ИТОГИ ТЕСТИРОВАНИЯ:")
    for test_name, result in results:
        print(f"{'✅' if result else '❌'} {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nПройдено: {passed}/{total} тестов")
    
    if passed == total:
        print("🎉 Все тесты пройдены!")
        sys.exit(0)
    else:
        print("⚠️ Некоторые тесты не пройдены")
        sys.exit(1)

if __name__ == "__main__":
    main()
