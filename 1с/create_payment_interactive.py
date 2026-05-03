# create_payment_interactive.py - создание оплаты по счёту (интерактивно) + авто-перезапуск IIS
import requests
import sys
import uuid
import json
import subprocess
import time
from datetime import datetime
from requests.auth import HTTPBasicAuth

# ============= НАСТРОЙКИ ПОДКЛЮЧЕНИЯ =============
BASE_URL = "http://localhost/1c/odata/standard.odata"
USE_AUTH = False
LOGIN = "your_login"
PASSWORD = "your_password"
TIMEOUT = 30
MAX_RETRIES = 3
# =================================================

def restart_iis():
    """Перезапуск IIS при ограничении учебной версии"""
    print("\n" + "="*60)
    print("[RESTART] Обнаружено ограничение учебной версии. Перезапускаем IIS...")
    print("="*60)
    try:
        result = subprocess.run(
            [sys.executable, "отключение_процесса_w3w.py"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        time.sleep(5)
        print("[OK] IIS перезапущен, продолжаем...\n")
        return True
    except Exception as e:
        print(f"[ERROR] Ошибка перезапуска: {e}")
        return False

def create_session():
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    if USE_AUTH:
        session.auth = HTTPBasicAuth(LOGIN, PASSWORD)
    return session

def get_unpaid_invoices(session):
    """Получает список неоплаченных счетов (СтатусСчета != 'Оплачен')"""
    url = f"{BASE_URL}/Document_СчетПокупателю"
    params = {"$filter": "СтатусСчета ne 'Оплачен'", "$top": 30}
    try:
        resp = session.get(url, params=params, timeout=TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('value', [])
        else:
            print(f"Ошибка получения счетов: {resp.status_code}")
            return []
    except Exception as e:
        print(f"Ошибка: {e}")
        return []

def display_invoices(invoices):
    """Показывает список счетов для выбора"""
    if not invoices:
        print("\n❌ Нет неоплаченных счетов!")
        return None
    print("\n📋 Доступные неоплаченные счета:")
    print("-" * 80)
    for idx, inv in enumerate(invoices, 1):
        number = inv.get('Number', 'Без номера')
        date = inv.get('Date', '')[:10] if inv.get('Date') else ''
        client = inv.get('Клиент', {}).get('Description') if inv.get('Клиент') else 'Неизвестно'
        total = inv.get('СуммаДокумента', 0)
        status = inv.get('СтатусСчета', 'Неизвестно')
        guid = inv.get('Ref_Key', '')
        print(f"  {idx}. Счёт №{number} от {date}")
        print(f"     Клиент: {client}")
        print(f"     Сумма: {total}")
        print(f"     Статус: {status}")
        print(f"     GUID: {guid}")
        print("-" * 80)
    return True

def select_invoice(invoices):
    """Позволяет пользователю выбрать счёт (по номеру или GUID)"""
    if not display_invoices(invoices):
        return None
    while True:
        choice = input("\nВыберите счёт (введите номер или GUID): ").strip()
        # Попробуем как GUID
        if len(choice) == 36 and choice.count('-') == 4:
            for inv in invoices:
                if inv.get('Ref_Key') == choice:
                    return inv
            print(f"❌ GUID '{choice}' не найден")
            continue
        # Попробуем как номер в списке
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(invoices):
                return invoices[idx]
            else:
                print(f"❌ Введите число от 1 до {len(invoices)}")
        except ValueError:
            print("❌ Введите номер или GUID счёта")

def send_payment_request(session, payment_data, retry_count=0):
    """Отправляет запрос на создание оплаты, автоматически перезапуская IIS при ограничении"""
    url = f"{BASE_URL}/Document_ОплатаПоСчету"
    try:
        resp = session.post(url, json=payment_data, timeout=TIMEOUT)
        print(f"Статус ответа (создание оплаты): {resp.status_code}")
        if resp.status_code in (200, 201):
            return resp, None
        if resp.status_code == 400:
            text_lower = resp.text.lower()
            if "ограничение учебной версии" in text_lower or "предельное количество подключений" in text_lower:
                print("\n⚠️ Достигнуто ограничение учебной версии!")
                if retry_count < MAX_RETRIES - 1:
                    if restart_iis():
                        new_session = create_session()
                        print(f"🔄 Повторная попытка {retry_count+2}/{MAX_RETRIES}")
                        return send_payment_request(new_session, payment_data, retry_count+1)
                return resp, "limit_exceeded"
        return resp, None
    except Exception as e:
        print(f"❌ Исключение: {e}")
        return None, "exception"

def post_payment(session, payment_guid, retry_count=0):
    """Проводит оплату через вызов /Post"""
    url = f"{BASE_URL}/Document_ОплатаПоСчету('{payment_guid}')/Post"
    body = {"PostingModeOperational": True}
    try:
        resp = session.post(url, json=body, timeout=TIMEOUT)
        print(f"Статус ответа (проведение оплаты): {resp.status_code}")
        if resp.status_code in (200, 204):
            return True, None
        if resp.status_code == 400:
            text_lower = resp.text.lower()
            if "ограничение учебной версии" in text_lower or "предельное количество подключений" in text_lower:
                if retry_count < MAX_RETRIES - 1:
                    if restart_iis():
                        new_session = create_session()
                        print(f"🔄 Повторная попытка проведения {retry_count+2}/{MAX_RETRIES}")
                        return post_payment(new_session, payment_guid, retry_count+1)
                return False, "limit_exceeded"
        return False, None
    except Exception as e:
        print(f"❌ Исключение при проведении: {e}")
        return False, "exception"

def main():
    print("\n" + "="*60)
    print("ОПЛАТА ПО СЧЁТУ В 1С")
    print("="*60)
    session = create_session()

    # 1. Получаем список неоплаченных счетов
    invoices = get_unpaid_invoices(session)
    if not invoices:
        print("❌ Не удалось получить счета или нет неоплаченных.")
        # Попробуем показать все счета без фильтра
        print("Пробуем получить все счета...")
        url = f"{BASE_URL}/Document_СчетПокупателю?$top=30"
        resp = session.get(url, timeout=TIMEOUT)
        if resp.status_code == 200:
            all_invoices = resp.json().get('value', [])
            if all_invoices:
                print("Найдены счета, но возможно поле СтатусСчета не используется.")
                invoices = all_invoices
            else:
                print("Нет ни одного счета.")
                return 1
        else:
            print(f"Ошибка получения счетов: {resp.status_code}")
            return 1

    # 2. Выбор счёта
    selected = select_invoice(invoices)
    if not selected:
        print("Отменено пользователем.")
        return 1

    invoice_guid = selected.get('Ref_Key')
    invoice_number = selected.get('Number', 'Без номера')
    invoice_sum = selected.get('СуммаДокумента', 0)
    print(f"\n✅ Выбран счёт №{invoice_number}, сумма: {invoice_sum}")

    # 3. Ввод суммы оплаты
    while True:
        try:
            amount = float(input(f"Введите сумму оплаты (до {invoice_sum}): ").strip())
            if amount <= 0:
                print("Сумма должна быть > 0")
                continue
            if amount > invoice_sum:
                print(f"Сумма не может превышать {invoice_sum}")
                continue
            break
        except ValueError:
            print("Введите число")

    # 4. Способ оплаты
    print("\nСпособы оплаты:")
    methods = ["Банковская карта", "Наличные", "Банковский перевод", "Электронные деньги"]
    for i, m in enumerate(methods, 1):
        print(f"  {i}. {m}")
    method_choice = input("Выберите способ (1-4, по умолчанию 1): ").strip()
    if method_choice in ['2','3','4']:
        payment_method = methods[int(method_choice)-1]
    else:
        payment_method = "Банковская карта"

    # 5. Опционально: комментарий
    comment = input("Комментарий (опционально): ").strip() or None

    # 6. Формируем данные оплаты
    payment_guid = str(uuid.uuid4())
    now = datetime.now().isoformat()
    payment_data = {
        "Ref_Key": payment_guid,
        "Date": now,
        "СуммаОплаты": amount,
        "СпособОплаты": payment_method,
        "ДатаПодтвержденияОплаты": now,
        "Счет_Key": invoice_guid
    }
    if comment:
        payment_data["Комментарий"] = comment

    # 7. Подтверждение
    print("\n" + "="*60)
    print("ПРОВЕРКА ДАННЫХ ОПЛАТЫ")
    print("="*60)
    print(f"Счёт: №{invoice_number} (GUID: {invoice_guid})")
    print(f"Сумма оплаты: {amount}")
    print(f"Способ: {payment_method}")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if comment:
        print(f"Комментарий: {comment}")
    confirm = input("\nСоздать и провести оплату? (д/н): ").strip().lower()
    if confirm not in ['д', 'да', 'y', 'yes']:
        print("Отменено")
        return 1

    # 8. Создаём оплату
    print("\n📡 Отправка данных в 1С...")
    resp, err = send_payment_request(session, payment_data)
    if resp is None or resp.status_code not in (200, 201):
        print("❌ Не удалось создать оплату.")
        if err == "limit_exceeded":
            print("Исчерпаны попытки перезапуска.")
        return 1
    print(f"✅ Оплата создана, GUID: {payment_guid}")

    # 9. Проводим оплату
    print("\n📡 Проведение оплаты...")
    success, err = post_payment(session, payment_guid)
    if success:
        print("✅ Оплата успешно проведена!")
    else:
        print("⚠️ Оплата создана, но не проведена. Проведите её позже вручную.")
        if err == "limit_exceeded":
            print("Причина: ограничение учебной версии. Попробуйте позже.")

    # 10. Обновляем статус счёта (если оплачена полная сумма)
    if amount >= invoice_sum:
        print("\n📡 Обновление статуса счёта на 'Оплачен'...")
        patch_url = f"{BASE_URL}/Document_СчетПокупателю('{invoice_guid}')"
        patch_data = {"СтатусСчета": "Оплачен"}
        try:
            patch_resp = session.patch(patch_url, json=patch_data, timeout=TIMEOUT)
            if patch_resp.status_code in (200, 204):
                print("✅ Статус счёта обновлён на 'Оплачен'")
            else:
                print(f"⚠️ Не удалось обновить статус счёта: {patch_resp.status_code}")
        except Exception as e:
            print(f"Ошибка обновления статуса: {e}")

    # Сохраняем результат
    result = {
        "success": True,
        "payment_guid": payment_guid,
        "invoice_guid": invoice_guid,
        "invoice_number": invoice_number,
        "amount": amount,
        "payment_method": payment_method,
        "date": now,
        "comment": comment
    }
    with open("created_payment.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\n📁 Результат сохранён в created_payment.json")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nПрервано пользователем")
        sys.exit(1)