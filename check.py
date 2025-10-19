# check.py
import os
import django
import sys

# Настройка Django
sys.path.append('/home/mihail/myshop')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')
django.setup()

from django.conf import settings

print('🔐 ПРОВЕРКА БЕЗОПАСНОСТИ')
print('=' * 30)

# Проверка ключа
if settings.SECRET_KEY.startswith('django-insecure-dev-key-only-'):
    print('❌ ИСПОЛЬЗУЕТСЯ ВРЕМЕННЫЙ КЛЮЧ ДЛЯ РАЗРАБОТКИ')
    print('⚠️  Это небезопасно для продакшена!')
else:
    print('✅ ИСПОЛЬЗУЕТСЯ ВАШ СЕКРЕТНЫЙ КЛЮЧ ИЗ .env')
    
# Дополнительная информация
print(f'📋 DEBUG: {settings.DEBUG}')
print(f'🌍 TIME_ZONE: {settings.TIME_ZONE}')
print(f'📁 ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')

print('=' * 30)
print('🎉 ВСЕ НАСТРОЙКИ КОРРЕКТНЫ!' if not settings.SECRET_KEY.startswith('django-insecure-dev-key-only-') else '⚠️  ТРЕБУЕТСЯ НАСТРОЙКА КЛЮЧА!')