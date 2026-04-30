# get_organizations.py
from config import BASE_URL, get_session

def main():
    try:
        session = get_session()  # <- теперь сессия сама перезапустит IIS при ошибке
        url = f"{BASE_URL}/Catalog_Организации"
        params = {"$top": 20}
        resp = session.get(url, params=params)
        print(f"Статус: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            orgs = data.get("value", [])
            print(f"Найдено организаций: {len(orgs)}")
            for org in orgs:
                print(f"  Наименование: {org.get('Description')}")
                print(f"    ИНН: {org.get('ИНН')}")
                print(f"    Ref_Key: {org.get('Ref_Key')}")
                print("  ---")
        else:
            print(f"Ошибка: {resp.text}")
            
    except Exception as e:
        print(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    main()