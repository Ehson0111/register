 # create_invoice_interactive.py — интерактивное создание счета покупателю
import requests
import sys
import uuid
from datetime import datetime
from requests.auth import HTTPBasicAuth

# ============= НАСТРОЙКИ ПОДКЛЮЧЕНИЯ =============
BASE_URL = "http://localhost/1c/odata/standard.odata"

USE_AUTH = False
LOGIN = "your_login"
PASSWORD = "your_password"

TIMEOUT = 30
# =================================================


def create_session():
    """Создаёт сессию с нужными заголовками"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    if USE_AUTH:
        session.auth = HTTPBasicAuth(LOGIN, PASSWORD)
    return session


def safe_int(value, default=0):
    """Безопасное преобразование в int"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    """Безопасное преобразование в float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def get_all_items(session, entity_name):
    """
    Получает все элементы справочника или документа.
    entity_name: например 'Catalog_Клиенты', 'Catalog_Услуги', 'Catalog_Организации'
    """
    url = f"{BASE_URL}/{entity_name}?$format=json"
    items = []
    
    while url:
        try:
            resp = session.get(url, timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            items.extend(data.get("value", []))
            url = data.get("@odata.nextLink")
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка при запросе {entity_name}: {e}")
            return []
    
    return items


def select_from_list(items, entity_type, display_field="Description"):
    """
    Показывает список и даёт пользователю выбрать один элемент.
    Возвращает выбранный элемент или None.
    """
    if not items:
        print(f"❌ Нет доступных элементов: {entity_type}")
        return None
    
    print(f"\n{'='*60}")
    print(f"ДОСТУПНЫЕ {entity_type.upper()}:")
    print(f"{'='*60}")
    
    for i, item in enumerate(items, 1):
        desc = item.get(display_field, "Без названия")
        ref = item.get("Ref_Key", "?")
        
        # Дополнительная информация в зависимости от типа
        extra_info = ""
        if entity_type == "Услуги":
            price = safe_int(item.get("Цена", 0))
            extra_info = f" | Цена: {price}"
        elif entity_type == "Клиенты":
            email = item.get("Email", "")
            phone = item.get("Телефон", "")
            extra_info = f" | Email: {email} | Тел: {phone}"
        elif entity_type == "Организации":
            inn = item.get("ИНН", "")
            extra_info = f" | ИНН: {inn}"
        
        print(f"{i:3}. {desc[:50]}{extra_info}")
        print(f"     GUID: {ref}")
    
    while True:
        try:
            choice = input(f"\nВыберите номер (1-{len(items)}) или 0 для отмены: ").strip()
            if choice == "0":
                return None
            choice_num = int(choice)
            if 1 <= choice_num <= len(items):
                selected = items[choice_num - 1]
                print(f"✅ Выбрано: {selected.get(display_field)}")
                return selected
            else:
                print(f"❌ Введите число от 1 до {len(items)}")
        except ValueError:
            print("❌ Введите корректное число")


def input_services(session):
    """
    Позволяет выбрать несколько услуг с количеством.
    Возвращает список словарей с услугой и количеством.
    """
    services = get_all_items(session, "Catalog_Услуги")
    if not services:
        return []
    
    selected_services = []
    
    while True:
        print(f"\n{'='*60}")
        print("ДОБАВЛЕНИЕ УСЛУГ В СЧЕТ")
        print(f"{'='*60}")
        print("Доступные услуги:")
        
        for i, service in enumerate(services, 1):
            desc = service.get("Description", "Без названия")
            price = safe_int(service.get("Цена", 0))
            print(f"{i:3}. {desc[:50]} | Цена: {price}")
            print(f"     GUID: {service.get('Ref_Key')}")
        
        choice = input(f"\nВыберите услугу (1-{len(services)}) или 0 для завершения: ").strip()
        
        if choice == "0":
            break
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(services):
                service = services[choice_num - 1]
                
                # Запрашиваем количество
                qty_input = input("Введите количество (по умолчанию 1): ").strip()
                quantity = safe_float(qty_input, 1.0)
                if quantity <= 0:
                    quantity = 1.0
                
                # Получаем цену и рассчитываем сумму
                price = safe_int(service.get("Цена", 0))
                total = price * quantity
                
                selected_services.append({
                    "service": service,
                    "quantity": quantity,
                    "price": price,
                    "total": total
                })
                
                print(f"✅ Добавлено: {service.get('Description')} x{quantity} = {total:.2f}")
            else:
                print(f"❌ Введите число от 1 до {len(services)}")
        except ValueError:
            print("❌ Введите корректное число")
    
    return selected_services


def create_invoice(session, organization_guid, client_guid, services_list, 
                   comment="", email_client=""):
    """
    Создаёт документ «Счет покупателю» с выбранными услугами.
    """
    invoice_guid = str(uuid.uuid4())
    
    # Рассчитываем общую сумму
    total_amount = sum(item["total"] for item in services_list)
    
    # Формируем состав счета (табличную часть)
    composition = []
    for i, item in enumerate(services_list):
        line = {
            "Ref_Key": invoice_guid,
            "LineNumber": i + 1,
            "Услуга_Key": item["service"]["Ref_Key"],
            "Количество": item["quantity"],
            "Цена": item["price"],
            "Сумма": item["total"]
        }
        composition.append(line)
    
    # Основные данные счета
    invoice_data = {
        "Ref_Key": invoice_guid,
        "Date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "Number": f"СЧ-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "Организация_Key": organization_guid,
        "Клиент_Key": client_guid,
        "СуммаДокумента": total_amount,
        "СтатусСчета": "НеОплачен",
        "Комментарий": comment,
        "EmailКлиента": email_client,
        "Posted": False,
        "DeletionMark": False,
        "Состав": composition
    }
    
    print(f"\n{'='*60}")
    print("СОЗДАНИЕ СЧЕТА ПОКУПАТЕЛЮ")
    print(f"{'='*60}")
    print(f"GUID счета: {invoice_guid}")
    print(f"Сумма: {total_amount:.2f}")
    print(f"Количество услуг: {len(services_list)}")
    print("-" * 60)
    
    try:
        resp = session.post(
            f"{BASE_URL}/Document_СчетПокупателю",
            json=invoice_data,
            timeout=TIMEOUT
        )
        
        if resp.status_code in (200, 201, 204):
            print("✅ СЧЕТ УСПЕШНО СОЗДАН!")
            print(f"   Номер: {invoice_data['Number']}")
            print(f"   Дата: {invoice_data['Date']}")
            print(f"   Сумма: {total_amount:.2f}")
            print(f"   Статус: НеОплачен")
            print(f"   GUID: {invoice_guid}")
            
            # Сохраняем результат в файл
            result = {
                "success": True,
                "type": "invoice",
                "ref_key": invoice_guid,
                "number": invoice_data["Number"],
                "date": invoice_data["Date"],
                "total_amount": total_amount,
                "organization_guid": organization_guid,
                "client_guid": client_guid,
                "services_count": len(services_list),
                "services": [
                    {
                        "name": item["service"].get("Description"),
                        "quantity": item["quantity"],
                        "price": item["price"],
                        "total": item["total"]
                    }
                    for item in services_list
                ]
            }
            
            with open("created_invoice.json", "w", encoding="utf-8") as f:
                import json
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print("📁 Результат сохранён в created_invoice.json")
            return invoice_guid
        else:
            print(f"❌ Ошибка при создании счета: {resp.status_code}")
            print(f"Ответ: {resp.text[:500]}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Сетевая ошибка: {e}")
        return None


def main():
    """Основная интерактивная функция"""
    print("=" * 60)
    print("ИНТЕРАКТИВНОЕ СОЗДАНИЕ СЧЕТА ПОКУПАТЕЛЮ В 1С")
    print("=" * 60)
    
    session = create_session()
    
    # === ШАГ 1: Выбор организации ===
    print("\n📋 ШАГ 1: Выбор организации")
    organizations = get_all_items(session, "Catalog_Организации")
    org = select_from_list(organizations, "Организации", "Description")
    
    if not org:
        print("❌ Организация не выбрана. Отмена.")
        return 1
    
    organization_guid = org["Ref_Key"]
    
    # === ШАГ 2: Выбор клиента ===
    print("\n📋 ШАГ 2: Выбор клиента")
    clients = get_all_items(session, "Catalog_Клиенты")
    client = select_from_list(clients, "Клиенты", "Description")
    
    if not client:
        print("❌ Клиент не выбран. Отмена.")
        return 1
    
    client_guid = client["Ref_Key"]
    client_email = client.get("Email", "")
    
    # === ШАГ 3: Выбор услуг ===
    print("\n📋 ШАГ 3: Добавление услуг")
    services_list = input_services(session)
    
    if not services_list:
        print("❌ Не выбрано ни одной услуги. Отмена.")
        return 1
    
    # === ШАГ 4: Дополнительная информация ===
    print(f"\n{'='*60}")
    print("ШАГ 4: Дополнительная информация")
    print(f"{'='*60}")
    
    comment = input("Комментарий к счету (опционально): ").strip()
    
    email = input(f"Email клиента [{client_email}]: ").strip()
    if not email:
        email = client_email
    
    # === ШАГ 5: Подтверждение и создание ===
    print(f"\n{'='*60}")
    print("ПРОВЕРКА ДАННЫХ ПЕРЕД СОЗДАНИЕМ")
    print(f"{'='*60}")
    print(f"Организация: {org.get('Description')}")
    print(f"Клиент: {client.get('Description')}")
    print(f"Email клиента: {email if email else 'не указан'}")
    print(f"Количество услуг: {len(services_list)}")
    
    total = sum(item["total"] for item in services_list)
    print(f"Общая сумма: {total:.2f}")
    print("-" * 60)
    
    for i, item in enumerate(services_list, 1):
        print(f"{i}. {item['service'].get('Description')} x{item['quantity']} = {item['total']:.2f}")
    
    print("-" * 60)
    
    confirm = input("Создать счет? (д/н): ").strip().lower()
    
    if confirm in ('д', 'да', 'y', 'yes'):
        invoice_guid = create_invoice(
            session,
            organization_guid,
            client_guid,
            services_list,
            comment,
            email
        )
        
        if invoice_guid:
            print(f"\n✅ Счет создан! GUID: {invoice_guid}")
            return 0
        else:
            print("\n❌ Не удалось создать счет")
            return 1
    else:
        print("Отменено пользователем")
        return 0


if __name__ == "__main__":
    sys.exit(main())