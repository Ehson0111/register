# create_client.py - создание нового клиента в 1С
import requests
import sys
import uuid
from requests.auth import HTTPBasicAuth

# ============= НАСТРОЙКИ ПОДКЛЮЧЕНИЯ =============
BASE_URL = "http://localhost/1c/odata/standard.odata"

# Если нужна авторизация - раскомментируйте и укажите логин/пароль
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

def create_client(description, email=None, phone=None, inn=None, client_type="Физическое лицо", crm_id=None):
    """
    Создаёт нового клиента в 1С
    
    Параметры:
        description (str): ФИО или наименование клиента (обязательно)
        email (str): Email клиента
        phone (str): Телефон клиента
        inn (int): ИНН клиента
        client_type (str): Тип клиента ("Физическое лицо"/"Юридическое лицо")
        crm_id (str): ID клиента в CRM системе
    
    Возвращает:
        dict: Информация о созданном клиенте или None при ошибке
    """
    session = create_session()
    
    # Генерируем новый GUID для клиента
    client_guid = str(uuid.uuid4())
    
    # Формируем данные для отправки
    client_data = {
        "Ref_Key": client_guid,
        "Description": description,
        "DeletionMark": False,
        "Predefined": False,
        "ТипКлиента": client_type
    }
    
    # Добавляем необязательные поля
    if email:
        client_data["Email"] = email
    if phone:
        client_data["Телефон"] = phone
    if inn:
        client_data["ИНН"] = inn
    if crm_id:
        client_data["CRM_ID"] = str(crm_id)
    
    print("="*60)
    print("СОЗДАНИЕ НОВОГО КЛИЕНТА")
    print("="*60)
    print(f"Наименование: {description}")
    print(f"Тип: {client_type}")
    if email:
        print(f"Email: {email}")
    if phone:
        print(f"Телефон: {phone}")
    if crm_id:
        print(f"CRM_ID: {crm_id}")
    print(f"GUID: {client_guid}")
    print("-"*60)
    
    try:
        resp = session.post(
            f"{BASE_URL}/Catalog_Клиенты",
            json=client_data,
            timeout=TIMEOUT
        )
        
        print(f"Статус ответа: {resp.status_code}")
        
        if resp.status_code in (200, 201):
            print("\n✅ УСПЕХ! Клиент успешно создан!")
            print(f"   Наименование: {description}")
            print(f"   Ref_Key (GUID): {client_guid}")
            
            # Сохраняем результат в файл
            result = {
                "success": True,
                "type": "client",
                "ref_key": client_guid,
                "description": description,
                "email": email,
                "phone": phone,
                "inn": inn,
                "client_type": client_type,
                "crm_id": crm_id
            }
            with open("created_client.json", "w", encoding="utf-8") as f:
                import json
                json.dump(result, f, ensure_ascii=False, indent=2)
            print("\n📁 Результат сохранён в created_client.json")
            return result
        else:
            print(f"\n❌ ОШИБКА! Не удалось создать клиента")
            print(f"Код: {resp.status_code}")
            print(f"Ответ: {resp.text[:500]}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения! Проверьте:")
        print("   1. Запущен ли сервер 1С")
        print("   2. Правильный ли адрес:", BASE_URL)
        return None
    except requests.exceptions.Timeout:
        print(f"❌ Таймаут! Сервер не ответил за {TIMEOUT} секунд")
        return None
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")
        return None

def main():
    """Основная функция с интерактивным вводом"""
    print("\nСОЗДАНИЕ КЛИЕНТА В 1С")
    print("="*60)
    
    # Запрашиваем данные у пользователя
    description = input("Введите ФИО/наименование клиента: ").strip()
    if not description:
        print("❌ Наименование клиента обязательно!")
        return 1
    
    email = input("Введите Email (опционально): ").strip()
    if not email:
        email = None
    
    phone = input("Введите телефон (опционально): ").strip()
    if not phone:
        phone = None
    
    print("Тип клиента:")
    print("  1 - Физическое лицо")
    print("  2 - Юридическое лицо")
    type_choice = input("Выберите тип (1/2, по умолчанию 1): ").strip()
    
    if type_choice == "2":
        client_type = "Юридическое лицо"
        inn = input("Введите ИНН (опционально): ").strip()
        if inn:
            try:
                inn = int(inn)
            except ValueError:
                print("❌ ИНН должен быть числом!")
                return 1
        else:
            inn = None
    else:
        client_type = "Физическое лицо"
        inn = None
    
    crm_id = input("Введите CRM_ID (опционально): ").strip()
    if not crm_id:
        crm_id = None
    
    print("\n" + "="*60)
    confirm = input("Создать клиента? (д/н): ").strip().lower()
    
    if confirm == 'д' or confirm == 'да' or confirm == 'y' or confirm == 'yes':
        result = create_client(description, email, phone, inn, client_type, crm_id)
        return 0 if result else 1
    else:
        print("Отменено")
        return 0

if __name__ == "__main__":
    sys.exit(main())