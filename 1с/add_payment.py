# # add_payment.py
# import sys
# import os
# import uuid
# from datetime import datetime
# from config import BASE_URL, get_session

# def main():
#     try:
#         # Читаем GUID последнего созданного счёта
#         if not os.path.exists('last_invoice_guid.txt'):
#             print("[ERROR] Нет сохранённого GUID счёта. Сначала создайте счёт через create_test_invoice.py")
#             return 1
        
#         with open('last_invoice_guid.txt', 'r') as f:
#             invoice_guid = f.read().strip()
        
#         print(f"[INFO] Создаём оплату для счёта: {invoice_guid}")
        
#         session = get_session()
#         payment_guid = str(uuid.uuid4())
        
#         payment_data = {
#             "Ref_Key": payment_guid,
#             "Date": datetime.now().isoformat(),
#             "СуммаОплаты": 1000,
#             "СпособОплаты": "Банковская карта",
#             "ДатаПодтвержденияОплаты": datetime.now().isoformat(),
#             "Счет_Key": invoice_guid
#         }
        
#         resp = session.post(f"{BASE_URL}/Document_ОплатаПоСчету", json=payment_data)
        
#         if resp.status_code in (200, 201):
#             print(f"[SUCCESS] Оплата создана, GUID: {payment_guid}")
            
#             # Проводим оплату
#             print("[INFO] Проводим оплату...")
#             url = f"{BASE_URL}/Document_ОплатаПоСчету('{payment_guid}')/StandardODATA.Post"
#             post_resp = session.post(url, json={"PostingModeOperational": True})
            
#             if post_resp.status_code in (200, 204):
#                 print("[SUCCESS] Оплата проведена успешно!")
#                 return 0
#             else:
#                 print(f"[WARNING] Оплата создана, но не проведена: {post_resp.status_code}")
#                 return 0
#         else:
#             print(f"[ERROR] Ошибка создания оплаты: {resp.status_code}")
#             print(resp.text)
#             return 1
            
#     except Exception as e:
#         print(f"[ERROR] Ошибка: {e}")
#         return 1

# if __name__ == "__main__":
#     sys.exit(main())    

# add_payment.py
# add_payment.py
import sys
import os
import uuid
from datetime import datetime
from config import BASE_URL, get_session

def main():
    if not os.path.exists('last_invoice_guid.txt'):
        print("[ERROR] Нет сохранённого GUID счёта. Сначала создайте счёт через create_test_invoice.py")
        return 1

    with open('last_invoice_guid.txt', 'r') as f:
        invoice_guid = f.read().strip()
    print(f"Создаём оплату для счёта: {invoice_guid}")

    session = get_session()
    payment_guid = str(uuid.uuid4())

    payment_data = {
        "Ref_Key": payment_guid,
        "Date": datetime.now().isoformat(),
        "СуммаОплаты": 1000,
        "СпособОплаты": "Банковская карта",
        "ДатаПодтвержденияОплаты": datetime.now().isoformat(),
        "Счет_Key": invoice_guid
    }

    resp = session.post(f"{BASE_URL}/Document_ОплатаПоСчету", json=payment_data)
    if resp.status_code not in (200, 201):
        print(f"[ERROR] Ошибка создания оплаты: {resp.status_code}")
        print(resp.text)
        return 1

    print(f"[SUCCESS] Оплата создана, GUID: {payment_guid}")

    # Проводим оплату
    post_url = f"{BASE_URL}/Document_ОплатаПоСчету('{payment_guid}')/Post"
    post_body = {"PostingModeOperational": True}
    post_resp = session.post(post_url, json=post_body)

    if post_resp.status_code in (200, 204):
        print("[SUCCESS] Оплата проведена успешно!")
        return 0
    else:
        print(f"[WARNING] Оплата создана, но не проведена. Код: {post_resp.status_code}")
        print(post_resp.text)
        return 0

if __name__ == "__main__":
    sys.exit(main())