"""
WSGI config for myshop project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')

# application = get_wsgi_application()

# Добавляем путь к вашему проекту
path = '/home/myshop'
if path not in sys.path:
    sys.path.append(path)

# Устанавливаем настройки для продакшена
os.environ['DJANGO_SETTINGS_MODULE'] = 'myshop.settings_production'

# Для корректных абсолютных URL и SEO
os.environ['SITE_URL'] = 'https://neboley.pythonanywhere.com'
os.environ['PYTHONANYWHERE_SITE'] = 'neboley.pythonanywhere.com'

# Для статических файлов
os.environ['PYTHONANYWHERE_DOMAIN'] = 'pythonanywhere.com'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()