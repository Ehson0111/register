# config.py
import requests
from requests.auth import HTTPBasicAuth
import subprocess
import sys
import time

BASE_URL = "http://localhost/1c/odata/standard.odata"

USE_AUTH = False
LOGIN = "your_login"
PASSWORD = "your_password"

def restart_iis():
    """Запускает скрипт перезапуска w3wp"""
    print("⚠️ Ошибка подключения к 1С (учебная версия). Перезапускаем IIS...")
    try:
        subprocess.run(
            [sys.executable, "отключение_процесса_w3w.py"],
            check=False
        )
        time.sleep(3)
        print("✅ IIS перезапущен")
        return True
    except Exception as e:
        print(f"❌ Ошибка перезапуска: {e}")
        return False

def get_session_with_retry():
    """Создаёт сессию с автоматическим перезапуском при ошибке"""
    max_retries = 3
    for attempt in range(max_retries):
        session = requests.Session()
        session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        if USE_AUTH:
            session.auth = HTTPBasicAuth(LOGIN, PASSWORD)
        
        # Тестовый запрос для проверки соединения
        try:
            test_resp = session.get(f"{BASE_URL}/Catalog_Услуги?$top=1", timeout=10)
            if test_resp.status_code == 200:
                return session
            elif test_resp.status_code == 500 and "ограничен" in test_resp.text.lower():
                raise Exception("Превышено ограничение учебной версии")
        except Exception as e:
            print(f"Попытка {attempt + 1} не удалась: {e}")
            if attempt < max_retries - 1:
                restart_iis()
                continue
            raise
    raise Exception("Не удалось создать сессию после перезапусков")

def get_session():
    """Основная функция получения сессии"""
    return get_session_with_retry()