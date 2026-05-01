
# # get_service_by_crm_id.py
# from config import BASE_URL, get_session

# def main():
#     session = get_session()
#     url = f"{BASE_URL}/Catalog_Услуги"
    
#     # Фильтр по CRM_ID = '4'
#     params = {
#         "$filter": f"crm_id eq '4'",
#         "$top": 1
#     }
    
#     print(f"Запрос: {url}")
#     print(f"Фильтр: crm_id eq '4'")
    
#     resp = session.get(url, params=params)
#     print(f"Статус: {resp.status_code}")
    
#     if resp.status_code == 200:
#         data = resp.json()
#         services = data.get('value', [])
        
#         if services:
#             service = services[0]
#             print("\n✅ Услуга найдена:")
#             print(f"  Наименование: {service.get('Description')}")
#             print(f"  Ref_Key (GUID): {service.get('Ref_Key')}")
#             print(f"  CRM_ID: {service.get('crm_id')}")
#             print(f"  Цена: {service.get('Цена')}")
#             print(f"  Активность: {service.get('Активность')}")
#             print(f"  Единица: {service.get('Единица')}")
#             print(f"  Код: {service.get('Code')}")
            
#             # Сохраняем GUID для дальнейшего использования
#             with open('service_guid.txt', 'w') as f:
#                 f.write(service.get('Ref_Key'))
#             print("\n💾 GUID услуги сохранён в service_guid.txt")
#         else:
#             print("\n❌ Услуга с CRM_ID='4' не найдена")
#             print("Проверьте, есть ли услуги с таким CRM_ID в базе")
            
#             # Показываем все услуги для проверки
#             print("\n📋 Все доступные услуги:")
#             all_resp = session.get(url, params={"$top": 10})
#             if all_resp.status_code == 200:
#                 all_services = all_resp.json().get('value', [])
#                 for s in all_services:
#                     print(f"  - {s.get('Description')} | CRM_ID: {s.get('crm_id')} | Ref_Key: {s.get('Ref_Key')[:8]}...")
#     else:
#         print(f"❌ Ошибка запроса: {resp.status_code}")
#         print(resp.text)

# if __name__ == "__main__":
#     main()