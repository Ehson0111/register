# test_service_by_crm_id.py - полностью автономный тест
import requests
import sys
import json
from requests.auth import HTTPBasicAuth

# ============= НАСТРОЙКИ ПОДКЛЮЧЕНИЯ =============
BASE_URL = "http://localhost/1c/odata/standard.odata"

# Если нужна авторизация - раскомментируйте и укажите логин/пароль
USE_AUTH = False
LOGIN = "your_login"
PASSWORD = "your_password"

# Таймаут запроса (секунды)
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

def get_service_by_crm_id(crm_id="4"):
    """Получает услугу по CRM_ID"""
    session = create_session()
    url = f"{BASE_URL}/Catalog_Услуги"
    
    # Пробуем фильтр
    params = {"$filter": f"crm_id eq '{crm_id}'", "$top": 1}
    
    print("="*60)
    print(f"ТЕСТ: Получение услуги с CRM_ID = {crm_id}")
    print("="*60)
    print(f"URL: {url}")
    print(f"Фильтр: crm_id eq '{crm_id}'")
    print("-"*60)
    
    try:
        resp = session.get(url, params=params, timeout=TIMEOUT)
        print(f"Статус ответа: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            services = data.get('value', [])
            
            if services:
                service = services[0]
                print("\n✅ УСПЕХ! Услуга найдена:")
                print(f"   Наименование: {service.get('Description')}")
                print(f"   Ref_Key (GUID): {service.get('Ref_Key')}")
                print(f"   CRM_ID: {service.get('crm_id')}")
                print(f"   Цена: {service.get('Цена')}")
                print(f"   Активность: {service.get('Активность')}")
                print(f"   Единица измерения: {service.get('Единица')}")
                print(f"   Код: {service.get('Code')}")
                
                # Сохраняем результат в файл
                result = {
                    "found": True,
                    "crm_id": crm_id,
                    "service": {
                        "ref_key": service.get('Ref_Key'),
                        "description": service.get('Description'),
                        "price": service.get('Цена'),
                        "activity": service.get('Активность'),
                        "unit": service.get('Единица')
                    }
                }
                with open("service_by_crm_id_result.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print("\n📁 Результат сохранён в service_by_crm_id_result.json")
                return 0
            else:
                print(f"\n❌ Услуга с CRM_ID='{crm_id}' НЕ НАЙДЕНА")
                
                # Показываем все услуги для проверки
                print("\n📋 Получаем все услуги для проверки...")
                all_resp = session.get(url, params={"$top": 10}, timeout=TIMEOUT)
                if all_resp.status_code == 200:
                    all_services = all_resp.json().get('value', [])
                    print(f"Найдено услуг в базе: {len(all_services)}")
                    print("\nСписок всех услуг:")
                    for s in all_services:
                        crm_id_val = s.get('crm_id')
                        print(f"   - {s.get('Description')[:30]:30} | CRM_ID: {crm_id_val} | GUID: {s.get('Ref_Key')[:8]}...")
                else:
                    print(f"Не удалось получить список услуг: {all_resp.status_code}")
                
                result = {"found": False, "crm_id": crm_id, "message": "Not found"}
                with open("service_by_crm_id_result.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                return 1
                
        elif resp.status_code == 500:
            print("\n⚠️ Ошибка 500 - возможно, фильтр не поддерживается")
            print("Пробуем получить все услуги и отфильтровать на стороне клиента...")
            
            # Альтернативный подход: получаем все услуги и фильтруем в Python
            all_resp = session.get(url, params={"$top": 50}, timeout=TIMEOUT)
            if all_resp.status_code == 200:
                all_services = all_resp.json().get('value', [])
                print(f"Получено услуг: {len(all_services)}")
                
                # Ищем услугу с нужным CRM_ID
                found_service = None
                for s in all_services:
                    if str(s.get('crm_id')) == str(crm_id):
                        found_service = s
                        break
                
                if found_service:
                    print("\n✅ УСПЕХ! Услуга найдена (фильтрация на клиенте):")
                    print(f"   Наименование: {found_service.get('Description')}")
                    print(f"   Ref_Key: {found_service.get('Ref_Key')}")
                    print(f"   CRM_ID: {found_service.get('crm_id')}")
                    print(f"   Цена: {found_service.get('Цена')}")
                    
                    result = {
                        "found": True,
                        "crm_id": crm_id,
                        "method": "client_side_filter",
                        "service": {
                            "ref_key": found_service.get('Ref_Key'),
                            "description": found_service.get('Description'),
                            "price": found_service.get('Цена')
                        }
                    }
                    with open("service_by_crm_id_result.json", "w", encoding="utf-8") as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    return 0
                else:
                    print(f"\n❌ Услуга с CRM_ID='{crm_id}' не найдена среди {len(all_services)} записей")
                    return 1
            else:
                print(f"Ошибка получения списка услуг: {all_resp.status_code}")
                return 1
        else:
            print(f"❌ Ошибка: {resp.status_code}")
            print(resp.text[:500])
            return 1
            
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения! Проверьте:")
        print("   1. Запущен ли сервер 1С")
        print("   2. Правильный ли адрес:", BASE_URL)
        print("   3. Открыт ли порт в firewall")
        return 1
    except requests.exceptions.Timeout:
        print(f"❌ Таймаут! Сервер не ответил за {TIMEOUT} секунд")
        return 1
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")
        return 1

def main():
    """Основная функция"""
    # Можно передать CRM_ID как аргумент командной строки
    if len(sys.argv) > 1:
        crm_id = sys.argv[1]
    else:
        crm_id = "4"
    
    return get_service_by_crm_id(crm_id)

if __name__ == "__main__":
    sys.exit(main())