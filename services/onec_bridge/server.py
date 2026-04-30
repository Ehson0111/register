import base64
import json
import os
import subprocess
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, quote, urlencode, urljoin
from urllib.request import Request, urlopen


# ========== ФУНКЦИЯ ДЛЯ ЛОГГИРОВАНИЯ ==========
def log(level, message):
    """Выводит лог с временной меткой"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [{level}] {message}")


# ========== ЧТЕНИЕ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ==========
log("INFO", "=== НАЧАЛО ЗАГРУЗКИ КОНФИГУРАЦИИ ===")

BRIDGE_HOST = os.getenv("ONEC_BRIDGE_HOST", "0.0.0.0")
BRIDGE_PORT = int(os.getenv("ONEC_BRIDGE_PORT", "8013"))
BRIDGE_SECRET = os.getenv("ONEC_BRIDGE_SECRET", "")
log("INFO", f"BRIDGE_HOST = {BRIDGE_HOST}")
log("INFO", f"BRIDGE_PORT = {BRIDGE_PORT}")
log("INFO", f"BRIDGE_SECRET = {'***' if BRIDGE_SECRET else '(не задан)'}")

ONEC_BASE_URL = os.getenv("ONEC_BASE_URL", "http://127.0.0.1/1c/odata/standard.odata/")
ONEC_USERNAME = os.getenv("ONEC_USERNAME", "")
ONEC_PASSWORD = os.getenv("ONEC_PASSWORD", "")
log("INFO", f"ONEC_BASE_URL = {ONEC_BASE_URL}")
log("INFO", f"ONEC_USERNAME = {'***' if ONEC_USERNAME else '(не задан)'}")
log("INFO", f"ONEC_PASSWORD = {'***' if ONEC_PASSWORD else '(не задан)'}")

ONEC_HEALTHCHECK_PATH = os.getenv("ONEC_HEALTHCHECK_PATH", "$metadata")
ONEC_USE_HEALTHCHECK = os.getenv("ONEC_USE_HEALTHCHECK", "false").lower() == "true"
ONEC_HEALTH_TIMEOUT_SECONDS = int(os.getenv("ONEC_HEALTH_TIMEOUT_SECONDS", "45"))
ONEC_HEALTHCHECK_TIMEOUT_SECONDS = int(os.getenv("ONEC_HEALTHCHECK_TIMEOUT_SECONDS", "10"))
ONEC_HEALTHCHECK_INTERVAL_SECONDS = float(os.getenv("ONEC_HEALTHCHECK_INTERVAL_SECONDS", "2"))
log("INFO", f"ONEC_HEALTHCHECK_PATH = {ONEC_HEALTHCHECK_PATH}")
log("INFO", f"ONEC_USE_HEALTHCHECK = {ONEC_USE_HEALTHCHECK}")
log("INFO", f"ONEC_HEALTH_TIMEOUT_SECONDS = {ONEC_HEALTH_TIMEOUT_SECONDS}")
log("INFO", f"ONEC_HEALTHCHECK_TIMEOUT_SECONDS = {ONEC_HEALTHCHECK_TIMEOUT_SECONDS}")
log("INFO", f"ONEC_HEALTHCHECK_INTERVAL_SECONDS = {ONEC_HEALTHCHECK_INTERVAL_SECONDS}")

ONEC_RESTART_SETTLE_SECONDS = float(os.getenv("ONEC_RESTART_SETTLE_SECONDS", "1.0"))
ONEC_RESTART_EACH_REQUEST = os.getenv("ONEC_RESTART_EACH_REQUEST", "true").lower() == "true"
ONEC_RESTART_COMMAND = os.getenv("ONEC_RESTART_COMMAND", "").strip()
ONEC_APP_POOL_NAME = os.getenv("ONEC_APP_POOL_NAME", "").strip()
ONEC_PROCESS_NAME = os.getenv("ONEC_PROCESS_NAME", "w3wp")
log("INFO", f"ONEC_RESTART_SETTLE_SECONDS = {ONEC_RESTART_SETTLE_SECONDS}")
log("INFO", f"ONEC_RESTART_EACH_REQUEST = {ONEC_RESTART_EACH_REQUEST}")
log("INFO", f"ONEC_RESTART_COMMAND = {ONEC_RESTART_COMMAND if ONEC_RESTART_COMMAND else '(не задана)'}")
log("INFO", f"ONEC_APP_POOL_NAME = {ONEC_APP_POOL_NAME if ONEC_APP_POOL_NAME else '(не задан)'}")
log("INFO", f"ONEC_PROCESS_NAME = {ONEC_PROCESS_NAME}")

ONEC_LIMIT_RETRY_ATTEMPTS = int(os.getenv("ONEC_LIMIT_RETRY_ATTEMPTS", "3"))
ONEC_LIMIT_RETRY_DELAY_SECONDS = float(os.getenv("ONEC_LIMIT_RETRY_DELAY_SECONDS", "1.5"))
log("INFO", f"ONEC_LIMIT_RETRY_ATTEMPTS = {ONEC_LIMIT_RETRY_ATTEMPTS}")
log("INFO", f"ONEC_LIMIT_RETRY_DELAY_SECONDS = {ONEC_LIMIT_RETRY_DELAY_SECONDS}")

CONNECTION_LIMIT_MARKERS = (
    "Достигнуто предельное количество подключений к ИБ",
    "Достигнуто ограничение учебной версии",
)
log("INFO", f"CONNECTION_LIMIT_MARKERS = {CONNECTION_LIMIT_MARKERS}")

log("INFO", "=== ЗАГРУЗКА КОНФИГУРАЦИИ ЗАВЕРШЕНА ===\n")


# ========== ФУНКЦИИ ==========
def build_auth_header():
    """Создает заголовок Basic авторизации"""
    log("DEBUG", "build_auth_header(): начало")
    if not ONEC_USERNAME and not ONEC_PASSWORD:
        log("DEBUG", "build_auth_header(): нет логина/пароля -> возвращаем None")
        return None
    token = base64.b64encode(f"{ONEC_USERNAME}:{ONEC_PASSWORD}".encode("utf-8")).decode("ascii")
    log("DEBUG", f"build_auth_header(): создан заголовок Basic {token[:10]}...")
    return f"Basic {token}"


def run_powershell(command):
    """Выполняет PowerShell команду"""
    log("INFO", f"run_powershell(): выполнение команды: {command[:100]}...")
    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if completed.returncode != 0:
            error_msg = completed.stderr.strip() or completed.stdout.strip() or "PowerShell command failed"
            log("ERROR", f"run_powershell(): ошибка (код {completed.returncode}): {error_msg}")
            raise RuntimeError(error_msg)
        log("INFO", f"run_powershell(): команда выполнена успешно")
        if completed.stdout:
            log("DEBUG", f"run_powershell(): stdout: {completed.stdout[:200]}")
        return completed
    except subprocess.TimeoutExpired:
        log("ERROR", "run_powershell(): таймаут 60 секунд")
        raise
    except Exception as e:
        log("ERROR", f"run_powershell(): исключение: {e}")
        raise


def restart_onec_runtime():
    """Перезапускает среду выполнения 1С"""
    log("INFO", "=== ПЕРЕЗАПУСК 1С ===")
    
    if ONEC_RESTART_COMMAND:
        log("INFO", f"restart_onec_runtime(): используем пользовательскую команду: {ONEC_RESTART_COMMAND}")
        run_powershell(ONEC_RESTART_COMMAND)
        log("INFO", "restart_onec_runtime(): пользовательская команда выполнена")
        return

    if ONEC_APP_POOL_NAME:
        log("INFO", f"restart_onec_runtime(): перезапускаем пул приложений IIS: {ONEC_APP_POOL_NAME}")
        run_powershell(f"Import-Module WebAdministration; Restart-WebAppPool -Name '{ONEC_APP_POOL_NAME}'")
        log("INFO", f"restart_onec_runtime(): пул {ONEC_APP_POOL_NAME} перезапущен")
        return

    log("INFO", f"restart_onec_runtime(): завершаем процесс: {ONEC_PROCESS_NAME}")
    run_powershell(
        f"Get-Process -Name '{ONEC_PROCESS_NAME}' -ErrorAction SilentlyContinue | Stop-Process -Force"
    )
    log("INFO", f"restart_onec_runtime(): процесс {ONEC_PROCESS_NAME} завершен")


def wait_until_available():
    """Ожидает доступности 1С после перезапуска"""
    log("INFO", f"=== ОЖИДАНИЕ ДОСТУПНОСТИ 1С (макс {ONEC_HEALTH_TIMEOUT_SECONDS} сек) ===")
    deadline = time.monotonic() + ONEC_HEALTH_TIMEOUT_SECONDS
    auth_header = build_auth_header()
    last_error = None
    attempt = 0
    
    while time.monotonic() < deadline:
        attempt += 1
        health_url = urljoin(f"{ONEC_BASE_URL.rstrip('/')}/", ONEC_HEALTHCHECK_PATH.lstrip("/"))
        log("DEBUG", f"wait_until_available(): попытка {attempt}, проверяем {health_url}")
        
        try:
            request = Request(health_url)
            if auth_header:
                request.add_header("Authorization", auth_header)
            request.add_header("Accept", "application/json")
            
            with urlopen(request, timeout=ONEC_HEALTHCHECK_TIMEOUT_SECONDS) as response:
                log("INFO", f"wait_until_available(): ответ {response.status} -> 1С доступна!")
                if response.status < 500:
                    return
                last_error = f"status={response.status}"
                log("WARNING", f"wait_until_available(): статус {response.status} (ожидался <500)")
        except Exception as exc:
            last_error = str(exc)
            log("WARNING", f"wait_until_available(): ошибка: {exc}")
        
        remaining = deadline - time.monotonic()
        log("DEBUG", f"wait_until_available(): ждем {ONEC_HEALTHCHECK_INTERVAL_SECONDS} сек, осталось {remaining:.1f} сек")
        time.sleep(ONEC_HEALTHCHECK_INTERVAL_SECONDS)
    
    error_msg = f"1С не ответила после перезапуска: {last_error or 'таймаут'}"
    log("ERROR", f"wait_until_available(): {error_msg}")
    raise RuntimeError(error_msg)


def prepare_after_restart():
    """Подготовка после перезапуска"""
    log("INFO", "=== ПОДГОТОВКА ПОСЛЕ ПЕРЕЗАПУСКА ===")
    if ONEC_USE_HEALTHCHECK:
        log("INFO", "prepare_after_restart(): используем healthcheck")
        wait_until_available()
    else:
        log("INFO", f"prepare_after_restart(): ждем {ONEC_RESTART_SETTLE_SECONDS} сек (healthcheck отключен)")
        time.sleep(ONEC_RESTART_SETTLE_SECONDS)
    log("INFO", "prepare_after_restart(): готовность завершена")


def build_target_url(base_url, path, params):
    """Строит целевой URL для запроса к 1С"""
    log("DEBUG", f"build_target_url(): base={base_url}, path={path}, params={params}")
    raw_path = path or ""
    embedded_query = ""
    if "?" in raw_path:
        raw_path, embedded_query = raw_path.split("?", 1)
        log("DEBUG", f"build_target_url(): обнаружены встроенные параметры: {embedded_query}")

    encoded_path = quote(raw_path, safe="/()'$,-._~:")
    target_url = urljoin(f"{base_url.rstrip('/')}/", encoded_path.lstrip("/"))
    log("DEBUG", f"build_target_url(): после кодирования пути: {target_url}")

    query_items = []
    if embedded_query:
        query_items.extend(parse_qsl(embedded_query, keep_blank_values=True))
        log("DEBUG", f"build_target_url(): добавлены встроенные параметры: {query_items}")

    for key, value in (params or {}).items():
        if isinstance(value, list):
            for item in value:
                query_items.append((key, item))
            log("DEBUG", f"build_target_url(): добавлен параметр {key}=[{', '.join(map(str, value))}]")
        else:
            query_items.append((key, value))
            log("DEBUG", f"build_target_url(): добавлен параметр {key}={value}")

    if query_items:
        target_url = f"{target_url}?{urlencode(query_items, doseq=True)}"
        log("DEBUG", f"build_target_url(): итоговый URL: {target_url}")
    else:
        log("DEBUG", f"build_target_url(): итоговый URL (без параметров): {target_url}")
    
    return target_url


def is_connection_limit_error(error_text):
    """Проверяет, является ли ошибка ошибкой лимита подключений"""
    if not error_text:
        log("DEBUG", "is_connection_limit_error(): error_text пуст -> False")
        return False
    
    for marker in CONNECTION_LIMIT_MARKERS:
        if marker in error_text:
            log("WARNING", f"is_connection_limit_error(): обнаружен маркер '{marker}' -> это ошибка лимита!")
            return True
    
    log("DEBUG", "is_connection_limit_error(): маркеры не найдены -> не ошибка лимита")
    return False


# ========== HTTP ОБРАБОТЧИК ==========
class OneCBridgeHandler(BaseHTTPRequestHandler):
    server_version = "OneCBridge/2.0"

    def log_message(self, format, *args):
        """Переопределяем логирование HTTP сервера"""
        log("HTTP", f"{self.address_string()} - {format % args}")

    def do_POST(self):
        """Обрабатывает POST запросы"""
        log("INFO", f"\n{'='*60}")
        log("INFO", f"=== НОВЫЙ POST ЗАПРОС ===")
        log("INFO", f"=== PATH: {self.path} ===")
        log("INFO", f"=== CLIENT: {self.client_address[0]}:{self.client_address[1]} ===")
        
        # Проверка секрета
        if BRIDGE_SECRET:
            client_secret = self.headers.get("X-Bridge-Secret", "")
            log("DEBUG", f"do_POST(): проверка секрета (ожидается {BRIDGE_SECRET[:10]}..., получено {client_secret[:10]}...)")
            if client_secret != BRIDGE_SECRET:
                log("WARNING", "do_POST(): неверный секрет -> 403")
                self._send_json({"detail": "forbidden"}, status=403)
                return
            log("DEBUG", "do_POST(): секрет верный")
        else:
            log("DEBUG", "do_POST(): секрет не требуется (BRIDGE_SECRET не задан)")

        try:
            # Чтение тела запроса
            content_length = int(self.headers.get("Content-Length", "0"))
            log("DEBUG", f"do_POST(): Content-Length = {content_length}")
            raw_body = self.rfile.read(content_length) if content_length else b"{}"
            log("DEBUG", f"do_POST(): тело запроса: {raw_body[:200]}...")
            
            payload = json.loads(raw_body.decode("utf-8") or "{}")
            log("INFO", f"do_POST(): распарсенный payload: operation={payload.get('operation')}")
            
            # Роутинг операций
            if self.path == "/invoice/create":
                response = self._create_invoice(payload)
            elif self.path == "/payment/register":
                response = self._register_payment(payload)
            elif self.path == "/invoke":
                # Обратная совместимость со старым API
                response = self._invoke_legacy(payload)
            else:
                log("WARNING", f"do_POST(): неверный путь '{self.path}' -> 404")
                self._send_json({"detail": "not found"}, status=404)
                return
            
            log("INFO", "do_POST(): запрос успешно выполнен, отправка ответа")
            self._send_json(response)
            
        except Exception as exc:
            log("ERROR", f"do_POST(): исключение: {exc}")
            self._send_json({"detail": str(exc)}, status=500)
        
        log("INFO", f"=== ЗАПРОС ОБРАБОТАН ===\n{'='*60}")

    def _create_invoice(self, payload):
        """Создание счета в 1С"""
        log("INFO", "\n=== СОЗДАНИЕ СЧЕТА В 1С ===")
        
        # Извлечение данных из payload
        crm_invoice_id = payload.get("crm_invoice_id")
        crm_deal_id = payload.get("crm_deal_id")
        customer_name = payload.get("customer_name")
        customer_email = payload.get("customer_email")
        service_name = payload.get("service_name")
        amount = payload.get("amount")
        comment = payload.get("comment", "")
        
        log("INFO", f"_create_invoice(): CRM Invoice ID = {crm_invoice_id}")
        log("INFO", f"_create_invoice(): CRM Deal ID = {crm_deal_id}")
        log("INFO", f"_create_invoice(): Customer = {customer_name}")
        log("INFO", f"_create_invoice(): Email = {customer_email}")
        log("INFO", f"_create_invoice(): Service = {service_name}")
        log("INFO", f"_create_invoice(): Amount = {amount}")
        
        # Валидация обязательных полей
        if not all([crm_invoice_id, crm_deal_id, customer_name, amount]):
            raise ValueError("Отсутствуют обязательные поля: crm_invoice_id, crm_deal_id, customer_name, amount")
        
        attempts = max(1, ONEC_LIMIT_RETRY_ATTEMPTS)
        last_error = None

        for attempt in range(1, attempts + 1):
            log("INFO", f"\n--- ПОПЫТКА СОЗДАНИЯ СЧЕТА {attempt}/{attempts} ---")
            
            # Перезапуск 1С если нужно
            if ONEC_RESTART_EACH_REQUEST:
                log("INFO", f"_create_invoice(): перезапуск перед запросом")
                restart_onec_runtime()
                prepare_after_restart()
            else:
                log("DEBUG", "_create_invoice(): перезапуск НЕ требуется")

            try:
                # Подготовка данных для создания счета
                invoice_data = {
                    "Number": f"CRM-{crm_invoice_id}",
                    "Date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                    "CRM_Invoice_ID": str(crm_invoice_id),
                    "CRM_Deal_ID": str(crm_deal_id),
                    "Organization_Key": "00000000-0000-0000-0000-000000000000",  # TODO: получить из настроек
                    "Customer": customer_name,
                    "Customer_Email": customer_email,
                    "Status": "НеОплачен",
                    "Amount": amount,
                    "Comment": comment,
                    "Services": [
                        {
                            "Service": service_name,
                            "Quantity": 1,
                            "Price": amount,
                            "Amount": amount
                        }
                    ]
                }
                
                # Создание счета через OData
                target_url = build_target_url(ONEC_BASE_URL, "Document_СчетПокупателю", {})
                body = json.dumps(invoice_data, ensure_ascii=False).encode("utf-8")
                
                headers = {
                    "Accept": "application/json;odata=verbose",
                    "Content-Type": "application/json; charset=utf-8"
                }
                
                auth_header = build_auth_header()
                if auth_header:
                    headers["Authorization"] = auth_header

                log("INFO", f"_create_invoice(): отправка POST запроса для создания счета")
                request = Request(target_url, data=body, headers=headers, method="POST")
                
                start_time = time.time()
                response = urlopen(request, timeout=30)
                elapsed = time.time() - start_time
                
                log("INFO", f"_create_invoice(): счет создан за {elapsed:.2f} сек, статус {response.status}")
                
                # Чтение ответа
                response_body = response.read().decode("utf-8")
                log("DEBUG", f"_create_invoice(): ответ 1С: {response_body[:300]}...")
                
                # Парсинг ответа для получения ID и номера
                response_data = json.loads(response_body)
                document_id = response_data.get("Ref_Key")
                document_number = response_data.get("Number")
                
                if not document_id:
                    raise RuntimeError("1С не вернула ID созданного документа")
                
                result = {
                    "success": True,
                    "document_id": document_id,
                    "document_number": document_number or f"CRM-{crm_invoice_id}",
                    "crm_invoice_id": crm_invoice_id,
                    "crm_deal_id": crm_deal_id,
                    "message": "Счет успешно создан в 1С"
                }
                
                log("INFO", f"_create_invoice(): успешное создание счета, ID = {document_id}")
                return result
                
            except Exception as exc:
                log("ERROR", f"_create_invoice(): ошибка при создании счета: {exc}")
                last_error = exc
                
                if attempt < attempts and is_connection_limit_error(str(exc)):
                    log("WARNING", f"_create_invoice(): обнаружена ошибка лимита подключений! Повтор через {ONEC_LIMIT_RETRY_DELAY_SECONDS} сек")
                    time.sleep(ONEC_LIMIT_RETRY_DELAY_SECONDS)
                    continue
                log("ERROR", "_create_invoice(): это не ошибка лимита или последняя попытка -> выбрасываем исключение")
                raise

        if last_error:
            log("ERROR", f"_create_invoice(): все попытки ({attempts}) провалились, последняя ошибка: {last_error}")
            raise last_error

    def _register_payment(self, payload):
        """Регистрация оплаты в 1С"""
        log("INFO", "\n=== РЕГИСТРАЦИЯ ОПЛАТЫ В 1С ===")
        
        # Извлечение данных из payload
        crm_invoice_id = payload.get("crm_invoice_id")
        onec_document_id = payload.get("onec_document_id")
        yookassa_payment_id = payload.get("yookassa_payment_id")
        amount = payload.get("amount")
        payment_date = payload.get("payment_date", datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
        payment_method = payload.get("payment_method", "yookassa")
        comment = payload.get("comment", "Оплата через YooKassa")
        
        log("INFO", f"_register_payment(): CRM Invoice ID = {crm_invoice_id}")
        log("INFO", f"_register_payment(): 1C Document ID = {onec_document_id}")
        log("INFO", f"_register_payment(): YooKassa Payment ID = {yookassa_payment_id}")
        log("INFO", f"_register_payment(): Amount = {amount}")
        log("INFO", f"_register_payment(): Payment Date = {payment_date}")
        
        # Валидация обязательных полей
        if not all([crm_invoice_id, onec_document_id, yookassa_payment_id, amount]):
            raise ValueError("Отсутствуют обязательные поля: crm_invoice_id, onec_document_id, yookassa_payment_id, amount")
        
        attempts = max(1, ONEC_LIMIT_RETRY_ATTEMPTS)
        last_error = None

        for attempt in range(1, attempts + 1):
            log("INFO", f"\n--- ПОПЫТКА РЕГИСТРАЦИИ ОПЛАТЫ {attempt}/{attempts} ---")
            
            # Перезапуск 1С если нужно
            if ONEC_RESTART_EACH_REQUEST:
                log("INFO", f"_register_payment(): перезапуск перед запросом")
                restart_onec_runtime()
                prepare_after_restart()
            else:
                log("DEBUG", "_register_payment(): перезапуск НЕ требуется")

            try:
                # Подготовка данных для создания оплаты
                payment_data = {
                    "Счет_Key": onec_document_id,
                    "CRM_Payment_ID": yookassa_payment_id,
                    "YooKassaPaymentID": yookassa_payment_id,
                    "Amount": amount,
                    "PaymentDate": payment_date,
                    "PaymentMethod": payment_method,
                    "Comment": comment,
                    "Posted": True  # Проводим документ сразу
                }
                
                # Создание оплаты через OData
                target_url = build_target_url(ONEC_BASE_URL, "Document_ОплатаПоСчету", {})
                body = json.dumps(payment_data, ensure_ascii=False).encode("utf-8")
                
                headers = {
                    "Accept": "application/json;odata=verbose",
                    "Content-Type": "application/json; charset=utf-8"
                }
                
                auth_header = build_auth_header()
                if auth_header:
                    headers["Authorization"] = auth_header

                log("INFO", f"_register_payment(): отправка POST запроса для создания оплаты")
                request = Request(target_url, data=body, headers=headers, method="POST")
                
                start_time = time.time()
                response = urlopen(request, timeout=30)
                elapsed = time.time() - start_time
                
                log("INFO", f"_register_payment(): оплата зарегистрирована за {elapsed:.2f} сек, статус {response.status}")
                
                # Чтение ответа
                response_body = response.read().decode("utf-8")
                log("DEBUG", f"_register_payment(): ответ 1С: {response_body[:300]}...")
                
                # Парсинг ответа
                response_data = json.loads(response_body)
                payment_document_id = response_data.get("Ref_Key")
                
                if not payment_document_id:
                    raise RuntimeError("1С не вернула ID созданного документа оплаты")
                
                # Обновление статуса счета на "Оплачен"
                self._update_invoice_status(onec_document_id, "Оплачен")
                
                result = {
                    "success": True,
                    "payment_document_id": payment_document_id,
                    "crm_invoice_id": crm_invoice_id,
                    "onec_document_id": onec_document_id,
                    "yookassa_payment_id": yookassa_payment_id,
                    "message": "Оплата успешно зарегистрирована в 1С"
                }
                
                log("INFO", f"_register_payment(): успешная регистрация оплаты, ID = {payment_document_id}")
                return result
                
            except Exception as exc:
                log("ERROR", f"_register_payment(): ошибка при регистрации оплаты: {exc}")
                last_error = exc
                
                if attempt < attempts and is_connection_limit_error(str(exc)):
                    log("WARNING", f"_register_payment(): обнаружена ошибка лимита подключений! Повтор через {ONEC_LIMIT_RETRY_DELAY_SECONDS} сек")
                    time.sleep(ONEC_LIMIT_RETRY_DELAY_SECONDS)
                    continue
                log("ERROR", "_register_payment(): это не ошибка лимита или последняя попытка -> выбрасываем исключение")
                raise

        if last_error:
            log("ERROR", f"_register_payment(): все попытки ({attempts}) провалились, последняя ошибка: {last_error}")
            raise last_error

    def _update_invoice_status(self, document_id, new_status):
        """Обновление статуса счета"""
        log("INFO", f"_update_invoice_status(): обновление статуса счета {document_id} на '{new_status}'")
        
        try:
            # Подготовка данных для обновления
            update_data = {
                "Status": new_status
            }
            
            target_url = build_target_url(ONEC_BASE_URL, f"Document_СчетПокупателю(guid'{document_id}')", {})
            body = json.dumps(update_data, ensure_ascii=False).encode("utf-8")
            
            headers = {
                "Accept": "application/json;odata=verbose",
                "Content-Type": "application/json; charset=utf-8"
            }
            
            auth_header = build_auth_header()
            if auth_header:
                headers["Authorization"] = auth_header

            request = Request(target_url, data=body, headers=headers, method="PATCH")
            
            with urlopen(request, timeout=30) as response:
                log("INFO", f"_update_invoice_status(): статус обновлен, код ответа {response.status}")
                
        except Exception as exc:
            log("ERROR", f"_update_invoice_status(): ошибка при обновлении статуса: {exc}")
            raise

    def _invoke_legacy(self, payload):
        """Обработка legacy запросов для обратной совместимости"""
        log("INFO", "\n=== LEGACY INVOKE ЗАПРОС ===")
        
        # Извлечение параметров
        method = payload.get("method", "GET").upper()
        path = payload.get("path", "")
        params = payload.get("params") or {}
        json_body = payload.get("json")
        timeout = payload.get("timeout", 20)
        restart_before_request = payload.get("restart_before_request", True)
        
        log("INFO", f"_invoke_legacy(): method = {method}")
        log("INFO", f"_invoke_legacy(): path = {path}")
        log("INFO", f"_invoke_legacy(): params = {params}")
        log("INFO", f"_invoke_legacy(): json_body = {'(есть)' if json_body else '(нет)'}")
        log("INFO", f"_invoke_legacy(): timeout = {timeout}")
        log("INFO", f"_invoke_legacy(): restart_before_request = {restart_before_request}")
        
        attempts = max(1, ONEC_LIMIT_RETRY_ATTEMPTS)
        last_error = None

        for attempt in range(1, attempts + 1):
            log("INFO", f"\n--- LEGACY ПОПЫТКА {attempt}/{attempts} ---")
            
            # Перезапуск 1С если нужно
            if restart_before_request and ONEC_RESTART_EACH_REQUEST:
                log("INFO", f"_invoke_legacy(): перезапуск перед запросом")
                restart_onec_runtime()
                prepare_after_restart()
            else:
                log("DEBUG", "_invoke_legacy(): перезапуск НЕ требуется")

            try:
                # Построение URL
                target_url = build_target_url(ONEC_BASE_URL, path, params)
                log("INFO", f"_invoke_legacy(): целевой URL: {target_url}")

                # Подготовка тела и заголовков
                body = None
                headers = {"Accept": "application/json;odata=verbose"}
                
                if json_body is not None:
                    body = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
                    headers["Content-Type"] = "application/json; charset=utf-8"
                    log("DEBUG", f"_invoke_legacy(): тело запроса: {body[:200]}...")
                
                auth_header = build_auth_header()
                if auth_header:
                    headers["Authorization"] = auth_header
                    log("DEBUG", "_invoke_legacy(): добавлен заголовок авторизации")

                log("INFO", f"_invoke_legacy(): отправка {method} запроса к 1С...")
                request = Request(target_url, data=body, headers=headers, method=method)
                
                start_time = time.time()
                response = urlopen(request, timeout=timeout)
                elapsed = time.time() - start_time
                
                log("INFO", f"_invoke_legacy(): запрос успешно выполнен за {elapsed:.2f} сек, статус {response.status}")
                
                # Чтение ответа
                response_body = response.read()
                log("INFO", f"_invoke_legacy(): размер ответа {len(response_body)} байт")
                
                return {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "body": response_body.decode("utf-8", errors="replace")
                }
                
            except Exception as exc:
                log("ERROR", f"_invoke_legacy(): ошибка: {exc}")
                last_error = exc
                
                if attempt < attempts and is_connection_limit_error(str(exc)):
                    log("WARNING", f"_invoke_legacy(): обнаружена ошибка лимита подключений! Повтор через {ONEC_LIMIT_RETRY_DELAY_SECONDS} сек")
                    time.sleep(ONEC_LIMIT_RETRY_DELAY_SECONDS)
                    continue
                log("ERROR", "_invoke_legacy(): последняя попытка -> выбрасываем исключение")
                raise

        if last_error:
            log("ERROR", f"_invoke_legacy(): все попытки ({attempts}) провалились, последняя ошибка: {last_error}")
            raise last_error

    def _send_json(self, payload, status=200):
        """Отправляет JSON ответ"""
        log("INFO", f"=== ОТПРАВКА JSON ОТВЕТА (статус {status}) ===")
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        log("DEBUG", f"_send_json(): тело: {body[:200]}...")
        
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        
        log("INFO", f"_send_json(): JSON ответ отправлен")


# ========== ЗАПУСК СЕРВЕРА ==========
if __name__ == "__main__":
    log("INFO", "\n" + "="*60)
    log("INFO", "=== ЗАПУСК 1C BRIDGE СЕРВЕРА v2.0 ===")
    log("INFO", "=== НОВЫЕ ENDPOINTS: ===")
    log("INFO", "=== POST /invoice/create - создание счета ===")
    log("INFO", "=== POST /payment/register - регистрация оплаты ===")
    log("INFO", "=== POST /invoke - legacy совместимость ===")
    log("INFO", "="*60)
    
    try:
        server = ThreadingHTTPServer((BRIDGE_HOST, BRIDGE_PORT), OneCBridgeHandler)
        log("INFO", f"Сервер запущен на http://{BRIDGE_HOST}:{BRIDGE_PORT}")
        log("INFO", "Ожидание входящих запросов...")
        log("INFO", "Нажмите Ctrl+C для остановки\n")
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        log("INFO", "\nПолучен сигнал остановки, завершаем работу...")
    except Exception as e:
        log("ERROR", f"Ошибка при запуске сервера: {e}")
