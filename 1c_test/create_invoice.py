# create_invoice.py (исправленная версия)
import uuid
from datetime import datetime
from config import BASE_URL, get_session

def main():
    # Получаем GUID из предыдущих запросов (или вводим вручную)
    SERVICE_GUID = input("Введите GUID услуги: ").strip()
    CLIENT_GUID = input("Введите GUID клиента: ").strip()
    ORG_GUID = input("Введите GUID организации: ").strip()
    
    session = get_session()  # автоматически перезапускает IIS при ошибке
    
    invoice_guid = str(uuid.uuid4())
    invoice_data = {
        "Ref_Key": invoice_guid,
        "Date": datetime.now().isoformat(),
        "Организация_Key": ORG_GUID,
        "Клиент_Key": CLIENT_GUID,
        "СуммаДокумента": 1000,
        "СтатусСчета": "НеОплачен",
        "Состав": [
            {
                "LineNumber": 1,
                "Услуга_Key": SERVICE_GUID,
                "Количество": 1,
                "Цена": 1000,
                "Сумма": 1000
            }
        ]
    }
    
    try:
        resp = session.post(f"{BASE_URL}/Document_СчетПокупателю", json=invoice_data)
        if resp.status_code in (200, 201):
            print(f"✅ Счёт создан! GUID: {invoice_guid}")
        else:
            print(f"❌ Ошибка: {resp.status_code}\n{resp.text}")
    except Exception as e:
        print(f"❌ Исключение: {e}")

if __name__ == "__main__":
    main()