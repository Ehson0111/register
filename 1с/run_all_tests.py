# run_all_tests.py
import subprocess
import sys
import time
import os
from datetime import datetime

# Список тестов для проверки (в порядке выполнения)
TESTS = [
    ("get_services.py", "Получение списка услуг"),
    ("get_clients.py", "Получение списка клиентов"),
    ("get_organizations.py", "Получение списка организаций"),
    ("create_test_invoice.py", "Создание тестового счёта"),
    ("post_invoice.py", "Проведение счёта"),
    ("add_payment.py", "Добавление оплаты"),
]

def restart_iis():
    """Перезапуск IIS при ошибке"""
    print("\n" + "="*60)
    print("[RESTART] Ограничение учебной версии! Перезапускаем IIS...")
    print("="*60)
    try:
        result = subprocess.run(
            [sys.executable, "отключение_процесса_w3w.py"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        time.sleep(5)
        print("[OK] IIS перезапущен, продолжаем тесты...\n")
        return True
    except Exception as e:
        print(f"[ERROR] Ошибка перезапуска: {e}")
        return False

def run_test(script_name, description, max_retries=3):
    """Запускает один тест с автоматическим перезапуском при ошибке"""
    print(f"\n{'-'*60}")
    print(f"[TEST] {description}")
    print(f"[SCRIPT] {script_name}")
    print(f"[TIME] {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'-'*60}")
    
    for attempt in range(max_retries):
        print(f"Attempt {attempt + 1}/{max_retries}")
        
        try:
            result = subprocess.run(
                [sys.executable, script_name],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("[STDERR]", result.stderr)
            
            if result.returncode == 0:
                print(f"[OK] {description} - SUCCESS")
                return True
            else:
                print(f"[FAIL] {description} - ERROR (code: {result.returncode})")
                
                error_text = (result.stdout + result.stderr).lower()
                if "ограничен" in error_text or "подключен" in error_text or "500" in error_text:
                    print("[WARN] Обнаружено ограничение учебной версии!")
                    if attempt < max_retries - 1:
                        if restart_iis():
                            continue
                
                return False
                
        except subprocess.TimeoutExpired:
            print(f"[TIMEOUT] Скрипт {script_name} выполнялся слишком долго")
            if attempt < max_retries - 1:
                restart_iis()
                continue
            return False
        except Exception as e:
            print(f"[ERROR] Критическая ошибка: {e}")
            return False
    
    print(f"[FAIL] {description} - FAILED after {max_retries} attempts")
    return False

def run_all_tests():
    """Запускает все тесты последовательно"""
    print("\n" + "="*60)
    print("[START] НАЧАЛО ТЕСТИРОВАНИЯ")
    print("="*60)
    print(f"[DATE] {datetime.now().strftime('%Y-%m-%d')}")
    print(f"[TIME] {datetime.now().strftime('%H:%M:%S')}")
    print("="*60)
    
    results = {}
    total_tests = len(TESTS)
    passed = 0
    
    for script_name, description in TESTS:
        if not os.path.exists(script_name):
            print(f"\n[WARN] Скрипт {script_name} не найден, пропускаем")
            results[description] = "SKIPPED (file not found)"
            continue
        
        success = run_test(script_name, description)
        results[description] = "PASSED" if success else "FAILED"
        if success:
            passed += 1
        
        time.sleep(2)
    
    print("\n" + "="*60)
    print("[RESULTS] РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("="*60)
    for test, result in results.items():
        print(f"{result} - {test}")
    
    print("="*60)
    print(f"TOTAL: {passed}/{total_tests} tests passed")
    
    if passed == total_tests:
        print("[SUCCESS] ВСЕ ТЕСТЫ УСПЕШНО ВЫПОЛНЕНЫ!")
        return 0
    else:
        print("[WARN] НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        return 1

if __name__ == "__main__":
    import ctypes
    
    if ctypes.windll.shell32.IsUserAnAdmin():
        print("[OK] Запущено с правами администратора")
        sys.exit(run_all_tests())
    else:
        print("[ERROR] Требуются права администратора для перезапуска IIS!")
        print("Как запустить от имени администратора:")
        print("1. Нажмите Win + R, введите 'cmd'")
        print("2. Нажмите Ctrl+Shift+Enter")
        print("3. Перейдите в папку: cd D:\\django\\crm\\1с")
        print("4. Запустите: python run_all_tests.py")
        sys.exit(1)