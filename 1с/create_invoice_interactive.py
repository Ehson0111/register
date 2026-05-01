# create_invoice_interactive.py - интерактивное создание счёта покупателю с авто-перезапуском IIS
import requests
import sys
import uuid
import json
import copy
import subprocess
import time
from datetime import datetime
from requests.auth import HTTPBasicAuth

# ============= НАСТРОЙКИ ПОДКЛЮЧЕНИЯ =============
BASE_URL = "http://localhost/1c/odata/standard.odata"
USE_AUTH = False
LOGIN = "your_login"
PASSWORD = "your_password"
TIMEOUT = 30
MAX_RETRIES = 3
# =================================================

def restart_iis():
    """Запускает скрипт перезапуска IIS (w3wp)"""
    print("\n" + "="*60)
    print("[RESTART] Обнаружено ограничение учебной версии. Перезапускаем IIS...")
    print("="*60)
    try:
        result = subprocess.run(
            [sys.executable, "отключение_процесса_w3w.py"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        time.sleep(5)
        print("[OK] IIS перезапущен, продолжаем...\n")
        return True
    except Exception as e:
        print(f"[ERROR] Ошибка перезапуска: {e}")
        return False

def create_session():
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    if USE_AUTH:
        session.auth = HTTPBasicAuth(LOGIN, PASSWORD)
    return session

def get_entity_list(endpoint):
    session = create_session()
    url = f"{BASE_URL}/{endpoint}"
    params = {"$top": 20}
    try:
        resp = session.get(url, params=params, timeout=TIMEOUT)
        if resp.status_code == 200:
            return resp.json().get('value', [])
        else:
            print(f"  Ошибка получения списка: {resp.status_code}")
            return []
    except Exception as e:
        print(f"  Ошибка: {e}")
        return []

def display_and_select(items, title, guid_field="Ref_Key", name_field="Description"):
    if not items:
        print(f"\n❌ Нет {title} в базе данных!")
        return None
    print(f"\n📋 Доступные {title}:")
    print("-" * 60)
    for idx, item in enumerate(items, 1):
        name = item.get(name_field, "Без наименования")
        guid = item.get(guid_field, "")
        print(f"  {idx}. {name}")
        print(f"     GUID: {guid}")
    print("-" * 60)
    while True:
        choice = input(f"\nВыберите {title} (введите номер или GUID): ").strip()
        if len(choice) == 36 and choice.count('-') == 4:
            for item in items:
                if item.get(guid_field) == choice:
                    return choice
            print(f"❌ GUID '{choice}' не найден в списке")
            continue
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                return items[idx].get(guid_field)
            else:
                print(f"❌ Неверный номер. Введите число от 1 до {len(items)}")
        except ValueError:
            print("❌ Введите номер или GUID (36 символов с дефисами)")

def input_invoice_items():
    items = []
    print("\n" + "="*60)
    print("ВВОД УСЛУГ (позиций счёта)")
    print("="*60)
    services = get_entity_list("Catalog_Услуги")
    if not services:
        print("❌ Нет услуг в базе! Сначала создайте услугу.")
        return None
    while True:
        print(f"\n--- Позиция {len(items) + 1} ---")
        service_guid = display_and_select(services, "услуг")
        if not service_guid:
            return None
        service_name = next((s.get('Description') for s in services if s.get('Ref_Key') == service_guid), "Неизвестно")
        while True:
            try:
                quantity = float(input("Введите количество: ").strip())
                if quantity <= 0:
                    print("❌ Количество должно быть больше 0")
                    continue
                break
            except ValueError:
                print("❌ Введите число (например, 2 или 1.5)")
        while True:
            try:
                price = float(input("Введите цену: ").strip())
                if price <= 0:
                    print("❌ Цена должна быть больше 0")
                    continue
                break
            except ValueError:
                print("❌ Введите число (например, 1000)")
        total = quantity * price
        items.append({
            "LineNumber": len(items) + 1,
            "Услуга_Key": service_guid,
            "Количество": quantity,
            "Цена": int(price) if price.is_integer() else price,
            "Сумма": int(total) if total.is_integer() else total,
            "service_name": service_name
        })
        print(f"\n✅ Добавлено: {service_name} | {quantity} x {price} = {total}")
        more = input("\nДобавить ещё услугу? (д/н): ").strip().lower()
        if more not in ['д', 'да', 'y', 'yes']:
            break
    return items

def send_invoice_request(invoice_data, session, retry_count=0):
    """Отправляет запрос на создание счёта с автоматическим перезапуском IIS при ограничении"""
    url = f"{BASE_URL}/Document_СчетПокупателю"
    try:
        resp = session.post(url, json=invoice_data, timeout=TIMEOUT)
        print(f"Статус ответа: {resp.status_code}")
        
        if resp.status_code == 200 or resp.status_code == 201:
            return resp, None  # успех
        elif resp.status_code == 400:
            # Проверяем, не связано ли с ограничением учебной версии
            text_lower = resp.text.lower()
            if "ограничение учебной версии" in text_lower or "предельное количество подключений" in text_lower:
                print("\n⚠️ Достигнуто ограничение учебной версии!")
                if retry_count < MAX_RETRIES - 1:
                    if restart_iis():
                        # Создаём новую сессию после перезапуска
                        new_session = create_session()
                        print(f"🔄 Повторная попытка {retry_count + 2}/{MAX_RETRIES}")
                        return send_invoice_request(invoice_data, new_session, retry_count + 1)
                return resp, "limit_exceeded"
        return resp, None
    except Exception as e:
        print(f"❌ Исключение: {e}")
        return None, "exception"

def create_invoice():
    print("\n" + "="*60)
    print("СОЗДАНИЕ СЧЁТА ПОКУПАТЕЛЮ")
    print("="*60)
    session = create_session()

    orgs = get_entity_list("Catalog_Организации")
    if not orgs:
        print("❌ Нет организаций в базе!")
        return None
    clients = get_entity_list("Catalog_Клиенты")
    if not clients:
        print("❌ Нет клиентов в базе!")
        return None

    org_guid = display_and_select(orgs, "организаций")
    if not org_guid:
        return None
    client_guid = display_and_select(clients, "клиентов")
    if not client_guid:
        return None

    items = input_invoice_items()
    if not items:
        return None

    print("\n" + "="*60)
    print("ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ (опционально)")
    print("="*60)
    email = input("Email клиента (опционально): ").strip() or None
    crm_invoice_id = input("CRM Invoice ID (ID счёта в вашей CRM, опционально): ").strip() or None
    crm_deal_id = input("CRM Deal ID (ID сделки в CRM, опционально): ").strip() or None
    comment = input("Комментарий к счёту (опционально): ").strip() or None

    total_sum = sum(item["Сумма"] for item in items)
    invoice_guid = str(uuid.uuid4())

    # Подготовка данных для отправки
    items_for_send = []
    for item in items:
        item_copy = {k: v for k, v in item.items() if k != "service_name"}
        items_for_send.append(item_copy)

    invoice_data = {
        "Ref_Key": invoice_guid,
        "Date": datetime.now().isoformat(),
        "Организация_Key": org_guid,
        "Клиент_Key": client_guid,
        "СуммаДокумента": total_sum,
        "СтатусСчета": "НеОплачен",
        "Состав": items_for_send
    }
    if email:
        invoice_data["EmailКлиента"] = email
    if crm_invoice_id:
        invoice_data["CRM_Invoice_ID"] = crm_invoice_id
    if crm_deal_id:
        invoice_data["CRM_Deal_ID"] = crm_deal_id
    if comment:
        invoice_data["Комментарий"] = comment

    # Показываем проверочные данные
    print("\n" + "="*60)
    print("ПРОВЕРКА ДАННЫХ")
    print("="*60)
    print(f"Организация GUID: {org_guid}")
    print(f"Клиент GUID: {client_guid}")
    print(f"Сумма счёта: {total_sum}")
    print(f"Количество позиций: {len(items)}")
    print("\nПозиции:")
    for item in items:
        print(f"  - {item['service_name']} | {item['Количество']} x {item['Цена']} = {item['Сумма']}")
    if email:
        print(f"Email: {email}")
    if crm_invoice_id:
        print(f"CRM Invoice ID: {crm_invoice_id}")
    if crm_deal_id:
        print(f"CRM Deal ID: {crm_deal_id}")

    print("\n" + "="*60)
    confirm = input("Создать счёт? (д/н): ").strip().lower()
    if confirm not in ['д', 'да', 'y', 'yes']:
        print("Отменено")
        return None

    print("\n📡 Отправка данных в 1С...")
    resp, err_flag = send_invoice_request(invoice_data, session)
    
    if resp is None:
        print("❌ Не удалось создать счёт из-за ошибки сети или исключения.")
        return None

    if resp.status_code in (200, 201):
        print("\n✅ УСПЕХ! Счёт успешно создан!")
        print(f"   GUID счёта: {invoice_guid}")
        print(f"   Сумма: {total_sum}")
        result = {
            "success": True,
            "invoice_guid": invoice_guid,
            "organization_guid": org_guid,
            "client_guid": client_guid,
            "total_sum": total_sum,
            "items_count": len(items),
            "items": items,
            "crm_invoice_id": crm_invoice_id,
            "crm_deal_id": crm_deal_id,
            "created_at": datetime.now().isoformat()
        }
        with open("created_invoice.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print("\n📁 Результат сохранён в created_invoice.json")
        post_choice = input("\nПровести счёт сейчас? (д/н): ").strip().lower()
        if post_choice in ['д', 'да', 'y', 'yes']:
            post_url = f"{BASE_URL}/Document_СчетПокупателю('{invoice_guid}')/Post"
            post_resp = session.post(post_url, json={"PostingModeOperational": True})
            if post_resp.status_code in (200, 204):
                print("✅ Счёт проведён!")
            else:
                print(f"⚠️ Не удалось провести счёт: {post_resp.status_code}")
        return result
    else:
        print(f"\n❌ ОШИБКА! Не удалось создать счёт")
        print(f"Код: {resp.status_code}")
        print(f"Ответ: {resp.text[:500]}")
        if err_flag == "limit_exceeded":
            print("Исчерпаны попытки перезапуска. Попробуйте позже.")
        return None

def main():
    return create_invoice()

if __name__ == "__main__":
    sys.exit(main() if main() else 1)