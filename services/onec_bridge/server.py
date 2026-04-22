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
    server_version = "OneCBridge/1.0"

    def log_message(self, format, *args):
        """Переопределяем логирование HTTP сервера"""
        log("HTTP", f"{self.address_string()} - {format % args}")

    def do_POST(self):
        """Обрабатывает POST запросы"""
        log("INFO", f"\n{'='*60}")
        log("INFO", f"=== НОВЫЙ POST ЗАПРОС ===")
        log("INFO", f"=== PATH: {self.path} ===")
        log("INFO", f"=== CLIENT: {self.client_address[0]}:{self.client_address[1]} ===")
        
        # Проверка пути
        if self.path != "/invoke":
            log("WARNING", f"do_POST(): неверный путь '{self.path}', ожидался '/invoke' -> 404")
            self._send_json({"detail": "not found"}, status=404)
            return
        
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
            log("INFO", f"do_POST(): распарсенный payload: method={payload.get('method')}, path={payload.get('path')}")
            
            # Вызов основной логики
            log("INFO", "do_POST(): вызов _invoke()")
            response = self._invoke(payload)
            
            log("INFO", "do_POST(): запрос успешно выполнен, отправка ответа")
            self._send_proxy_response(response)
            
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            log("ERROR", f"do_POST(): HTTPError {exc.code}: {body[:200]}")
            self._send_json({"detail": body or str(exc)}, status=exc.code)
        except URLError as exc:
            log("ERROR", f"do_POST(): URLError: {exc.reason}")
            self._send_json({"detail": str(exc.reason)}, status=502)
        except Exception as exc:
            log("ERROR", f"do_POST(): исключение: {exc}")
            self._send_json({"detail": str(exc)}, status=500)
        
        log("INFO", f"=== ЗАПРОС ОБРАБОТАН ===\n{'='*60}")

    def _invoke(self, payload):
        """Основная логика выполнения запроса к 1С"""
        log("INFO", "\n=== ВЫПОЛНЕНИЕ ЗАПРОСА К 1С ===")
        
        # Извлечение параметров
        method = payload.get("method", "GET").upper()
        path = payload.get("path", "")
        params = payload.get("params") or {}
        json_body = payload.get("json")
        timeout = payload.get("timeout", 20)
        restart_before_request = payload.get("restart_before_request", True)
        
        log("INFO", f"_invoke(): method = {method}")
        log("INFO", f"_invoke(): path = {path}")
        log("INFO", f"_invoke(): params = {params}")
        log("INFO", f"_invoke(): json_body = {'(есть)' if json_body else '(нет)'}")
        log("INFO", f"_invoke(): timeout = {timeout}")
        log("INFO", f"_invoke(): restart_before_request = {restart_before_request}")
        
        attempts = max(1, ONEC_LIMIT_RETRY_ATTEMPTS)
        log("INFO", f"_invoke(): максимальное количество попыток = {attempts}")
        
        last_error = None

        for attempt in range(1, attempts + 1):
            log("INFO", f"\n--- ПОПЫТКА {attempt}/{attempts} ---")
            
            # Перезапуск 1С если нужно
            if restart_before_request and ONEC_RESTART_EACH_REQUEST:
                log("INFO", f"_invoke(): перезапуск перед запросом (restart_before_request={restart_before_request}, ONEC_RESTART_EACH_REQUEST={ONEC_RESTART_EACH_REQUEST})")
                restart_onec_runtime()
                prepare_after_restart()
            else:
                log("DEBUG", "_invoke(): перезапуск НЕ требуется")

            try:
                # Построение URL
                target_url = build_target_url(ONEC_BASE_URL, path, params)
                log("INFO", f"_invoke(): целевой URL: {target_url}")

                # Подготовка тела и заголовков
                body = None
                headers = {"Accept": "application/json;odata=verbose"}
                
                if json_body is not None:
                    body = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
                    headers["Content-Type"] = "application/json; charset=utf-8"
                    log("DEBUG", f"_invoke(): тело запроса: {body[:200]}...")
                
                auth_header = build_auth_header()
                if auth_header:
                    headers["Authorization"] = auth_header
                    log("DEBUG", "_invoke(): добавлен заголовок авторизации")

                log("INFO", f"_invoke(): отправка {method} запроса к 1С...")
                request = Request(target_url, data=body, headers=headers, method=method)
                
                start_time = time.time()
                response = urlopen(request, timeout=timeout)
                elapsed = time.time() - start_time
                
                log("INFO", f"_invoke(): запрос успешно выполнен за {elapsed:.2f} сек, статус {response.status}")
                return response
                
            except HTTPError as exc:
                body_text = exc.read().decode("utf-8", errors="replace")
                log("ERROR", f"_invoke(): HTTPError {exc.code}: {body_text[:300]}")
                last_error = exc
                
                if attempt < attempts and is_connection_limit_error(body_text):
                    log("WARNING", f"_invoke(): обнаружена ошибка лимита подключений! Повтор через {ONEC_LIMIT_RETRY_DELAY_SECONDS} сек")
                    time.sleep(ONEC_LIMIT_RETRY_DELAY_SECONDS)
                    continue
                log("ERROR", "_invoke(): это не ошибка лимита или последняя попытка -> выбрасываем исключение")
                raise
                
            except URLError as exc:
                log("ERROR", f"_invoke(): URLError: {exc.reason}")
                last_error = exc
                if attempt < attempts:
                    log("WARNING", f"_invoke(): ошибка соединения, повтор через {ONEC_LIMIT_RETRY_DELAY_SECONDS} сек")
                    time.sleep(ONEC_LIMIT_RETRY_DELAY_SECONDS)
                    continue
                log("ERROR", "_invoke(): последняя попытка -> выбрасываем исключение")
                raise
            
            except Exception as exc:
                log("ERROR", f"_invoke(): непредвиденная ошибка: {exc}")
                raise

        if last_error:
            log("ERROR", f"_invoke(): все попытки ({attempts}) провалились, последняя ошибка: {last_error}")
            raise last_error
        
        log("ERROR", "_invoke(): неизвестная ошибка")
        raise RuntimeError("Не удалось выполнить запрос в 1С.")

    def _send_proxy_response(self, response):
        """Отправляет ответ от 1С обратно клиенту"""
        log("INFO", "=== ОТПРАВКА ОТВЕТА КЛИЕНТУ ===")
        body = response.read()
        log("INFO", f"_send_proxy_response(): статус {response.status}, размер тела {len(body)} байт")
        
        self.send_response(response.status)
        content_type = response.headers.get("Content-Type", "application/json")
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        
        log("INFO", f"_send_proxy_response(): ответ отправлен (Content-Type: {content_type})")

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
    log("INFO", "=== ЗАПУСК 1C BRIDGE СЕРВЕРА ===")
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