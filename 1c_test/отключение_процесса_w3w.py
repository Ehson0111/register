import subprocess
import sys
import ctypes

def is_admin():
    """Проверка, запущен ли скрипт от имени администратора"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def restart_iis():
    """Полный перезапуск IIS (все пулы, все процессы w3wp)"""
    print("🔄 Перезапуск IIS...")
    try:
        # iisreset — стандартная команда Windows для перезапуска IIS
        result = subprocess.run(['iisreset'], capture_output=True, text=True, encoding='cp866')
        if result.returncode == 0:
            print("✅ IIS успешно перезапущен")
            return True
        else:
            print(f"❌ Ошибка iisreset: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Команда 'iisreset' не найдена. Возможно, IIS не установлен.")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def kill_w3wp():
    """Принудительно завершить все процессы w3wp.exe (если iisreset не работает)"""
    print("🔪 Принудительное завершение w3wp.exe...")
    try:
        result = subprocess.run(
            ['taskkill', '/F', '/IM', 'w3wp.exe'],
            capture_output=True,
            text=True,
            encoding='cp866'
        )
        if result.returncode == 0:
            print("✅ Все процессы w3wp.exe завершены")
        elif "not found" in result.stderr.lower():
            print("ℹ️ Процессы w3wp.exe не найдены (возможно, IIS не запущен)")
        else:
            print(f"⚠️ {result.stderr}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    if not is_admin():
        print("❌ Этот скрипт требует прав администратора!")
        print("   Пожалуйста, запустите PowerShell или командную строку от имени администратора")
        print("   и выполните команду: python отключение_процесса_w3w.py")
        sys.exit(1)
    
    print("=" * 50)
    print("Управление процессами IIS (w3wp.exe)")
    print("=" * 50)
    
    # Пробуем перезапустить IIS полностью (рекомендуемый способ)
    if not restart_iis():
        # Если iisreset не сработал — убиваем процессы вручную
        print("\nПерезапуск IIS не удался, пробуем принудительно завершить процессы...")
        kill_w3wp()