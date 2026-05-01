# create_service_fast.py - быстрое создание услуги с параметрами командной строки
import requests
import sys
import uuid
import json
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost/1c/odata/standard.odata"
USE_AUTH = False
LOGIN = "your_login"
PASSWORD = "your_password"

def create_session():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
    if USE_AUTH:
        session.auth = HTTPBasicAuth(LOGIN, PASSWORD)
    return session

def create_service(description, price, unit="шт", activity="Да", crm_id=None):
    session = create_session()
    service_guid = str(uuid.uuid4())
    
    service_data = {
        "Ref_Key": service_guid,
        "Description": description,
        "Цена": price,
        "Единица": unit,
        "Активность": activity,
        "DeletionMark": False
    }
    if crm_id:
        service_data["crm_id"] = str(crm_id)
    
    resp = session.post(f"{BASE_URL}/Catalog_Услуги", json=service_data)
    
    if resp.status_code in (200, 201):
        result = {"success": True, "ref_key": service_guid, "description": description}
        with open("created_service.json", "w") as f:
            json.dump(result, f, indent=2)
        print(f"✅ Услуга создана! GUID: {service_guid}")
        return service_guid
    else:
        print(f"❌ Ошибка: {resp.status_code}")
        print(resp.text)
        return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование: python create_service_fast.py <наименование> <цена> [CRM_ID]")
        print("Пример: python create_service_fast.py 'Консультация' 5000 123")
        sys.exit(1)
    
    name = sys.argv[1]
    price = int(sys.argv[2])
    crm_id = sys.argv[3] if len(sys.argv) > 3 else None
    
    create_service(name, price, crm_id=crm_id)