# get_clients.py
from config import BASE_URL, get_session

def main():
    session = get_session()
    url = f"{BASE_URL}/Catalog_Клиенты"
    params = {"$top": 20}  # первые 20 записей
    resp = session.get(url, params=params)
    print(f"Статус: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        clients = data.get("value", [])
        print(f"Найдено клиентов: {len(clients)}")
        for client in clients:
            print(f"  Наименование: {client.get('Description')}")
            print(f"    Email: {client.get('Email')}")
            print(f"    Телефон: {client.get('Телефон')}")
            print(f"    Ref_Key (GUID): {client.get('Ref_Key')}")
            print(f"    CRM_ID: {client.get('CRM_ID')}")
            print("  ---")
    else:
        print(f"Ошибка: {resp.text}")

if __name__ == "__main__":
    main()