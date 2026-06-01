import requests
from requests.auth import HTTPBasicAuth

# ========= НАСТРОЙКИ =========
BASE_URL = "http://localhost/1c/odata/standard.odata"
USE_AUTH = False          # измените на True, если нужна авторизация
LOGIN = "user"
PASSWORD = "password"

# GUID счёта, который нужно оплатить (замените на нужный)
INVOICE_GUID = "3b1143a6-550d-4670-9915-5562c5def4ff"
NEW_STATUS = "Оплачен"    # или "НеОплачен"
# =============================

session = requests.Session()
session.headers.update({
    "Content-Type": "application/json",
    "Accept": "application/json"
})
if USE_AUTH:
    session.auth = HTTPBasicAuth(LOGIN, PASSWORD)

url = f"{BASE_URL}/Document_СчетПокупателю(guid'{INVOICE_GUID}')"
payload = {"СтатусСчета": NEW_STATUS}

try:
    resp = session.patch(url, json=payload, timeout=30)
    if resp.status_code in (200, 204):
        print(f"✅ Статус счёта {INVOICE_GUID} изменён на «{NEW_STATUS}»")
    else:
        print(f"❌ Ошибка {resp.status_code}: {resp.text[:200]}")
except Exception as e:
    print(f"❌ Не удалось выполнить запрос: {e}")