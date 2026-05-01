# post_invoice.py
import sys
import os
from config import BASE_URL, get_session

def main():
    if not os.path.exists('last_invoice_guid.txt'):
        print("[ERROR] Нет сохранённого GUID счёта. Сначала создайте счёт через create_test_invoice.py")
        return 1

    with open('last_invoice_guid.txt', 'r') as f:
        invoice_guid = f.read().strip()
    print(f"Проводим счёт: {invoice_guid}")

    session = get_session()
    url = f"{BASE_URL}/Document_СчетПокупателю('{invoice_guid}')/Post"
    body = {"PostingModeOperational": True}

    try:
        resp = session.post(url, json=body)
        if resp.status_code in (200, 204):
            print("[SUCCESS] Счёт успешно проведён!")
            return 0
        else:
            print(f"[ERROR] Ошибка проведения: {resp.status_code}")
            print(resp.text)
            return 1
    except Exception as e:
        print(f"[ERROR] Исключение: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())