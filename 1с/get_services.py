# get_services.py
import json
from config import BASE_URL, get_session

def main():
    session = get_session()
    url = f"{BASE_URL}/Catalog_Услуги"
    # Убираем $filter, оставляем только $top
    params = {"$top": 10}
    
    resp = session.get(url, params=params)
    print(f"Статус: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        services = data.get('value', [])
        print(f"Найдено услуг: {len(services)}")
        for item in services:
            # Поля из метаданных: Description, Цена, Активность и т.д.
            print(f"  - {item.get('Description')} (Цена: {item.get('Цена')}, Активность: {item.get('Активность')}, Ref_Key: {item.get('Ref_Key')})")
    else:
        print(f"Ошибка: {resp.text}")

if __name__ == "__main__":
    main()