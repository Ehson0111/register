import os
import django
from pathlib import Path

# Установите правильный путь
project_path = Path(__file__).resolve().parent
os.chdir(project_path)

#asf Настройте Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    django.setup()
    print("✅ Django setup successful")
    
    # Проверьте настройки о
    from django.conf import settings
    print(f"✅ DEBUG mode: {settings.DEBUG}")
    print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"✅ INSTALLED_APPS: {len(settings.INSTALLED_APPS)} apps")
    
    # Проверьте базу данных
    from django.db import connection
    connection.ensure_connection()
    print("✅ Database connection successful")
    
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    import traceback
    traceback.print_exc()