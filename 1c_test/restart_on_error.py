# restart_on_error.py
import subprocess
import time
import sys

def restart_iis():
    """Запускает скрипт перезапуска w3wp"""
    print("⚠️ Обнаружена ошибка подключения к 1С. Перезапускаем IIS...")
    try:
        # Запускаем ваш скрипт отключения w3w
        result = subprocess.run(
            [sys.executable, "отключение_процесса_w3w.py"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        time.sleep(3)  # Даём время на перезапуск
        return True
    except Exception as e:
        print(f"❌ Ошибка при перезапуске: {e}")
        return False

def with_restart_on_error(func):
    """Декоратор: при ошибке перезапускает IIS и повторяет запрос"""
    def wrapper(*args, **kwargs):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = func(*args, **kwargs)
                if result is not None:
                    return result
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                if attempt < max_retries - 1:
                    if restart_iis():
                        print(f"🔄 Повторная попытка {attempt + 2}/{max_retries}")
                        continue
                print(f"❌ Не удалось выполнить после {max_retries} попыток")
                return None
        return None
    return wrapper