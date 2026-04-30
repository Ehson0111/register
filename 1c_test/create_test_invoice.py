# create_test_invoice.py
import sys
import uuid
from datetime import datetime
from config import BASE_URL, get_session

def main():
    try:
        session = get_session()
        
        print("[1] Получаем GUID из справочников...")
        
        # Получаем первую услугу
        resp = session.get(f"{BASE_URL}/Catalog_Услуги?$top=1")
        if resp.status_code != 200:
            print("[ERROR] Не удалось получить услугу")
            return 1
        services = resp.json().get('value', [])
        if not services:
            print("[ERROR] Нет услуг в справочнике")
            return 1
        service_guid = services[0]['Ref_Key']
        print(f"  [OK] Услуга: {services[0].get('Description')} ({service_guid})")
        
        # Получаем первого клиента
        resp = session.get(f"{BASE_URL}/Catalog_Клиенты?$top=1")
        if resp.status_code != 200:
            print("[ERROR] Не удалось получить клиента")
            return 1
        clients = resp.json().get('value', [])
        if not clients:
            print("[ERROR] Нет клиентов в справочнике")
            return 1
        client_guid = clients[0]['Ref_Key']
        print(f"  [OK] Клиент: {clients[0].get('Description')} ({client_guid})")
        
        # Получаем первую организацию
        resp = session.get(f"{BASE_URL}/Catalog_Организации?$top=1")
        if resp.status_code != 200:
            print("[ERROR] Не удалось получить организацию")
            return 1
        orgs = resp.json().get('value', [])
        if not orgs:
            print("[ERROR] Нет организаций в справочнике")
            return 1
        org_guid = orgs[0]['Ref_Key']
        print(f"  [OK] Организация: {orgs[0].get('Description')} ({org_guid})")
        
        # Создаём счёт
        invoice_guid = str(uuid.uuid4())
        invoice_data = {
            "Ref_Key": invoice_guid,
            "Date": datetime.now().isoformat(),
            "Организация_Key": org_guid,
            "Клиент_Key": client_guid,
            "СуммаДокумента": 1000,
            "СтатусСчета": "НеОплачен",
            "Состав": [
                {
                    "LineNumber": 1,
                    "Услуга_Key": service_guid,
                    "Количество": 1,
                    "Цена": int(services[0].get('Цена', 1000)),
                    "Сумма": 1000
                }
            ]
        }
        
        print("[2] Создаём счёт...")
        resp = session.post(f"{BASE_URL}/Document_СчетПокупателю", json=invoice_data)
        
        if resp.status_code in (200, 201):
            print(f"[SUCCESS] Счёт успешно создан! GUID: {invoice_guid}")
            # Сохраняем GUID для следующих тестов
            with open('last_invoice_guid.txt', 'w') as f:
                f.write(invoice_guid)
            return 0
        else:
            print(f"[ERROR] Ошибка создания: {resp.status_code}")
            print(resp.text)
            return 1
            
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())