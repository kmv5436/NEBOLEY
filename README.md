# MyShop - Интернет-магазин на Django

- 📦 Каталог товаров с категориями и фильтрами
- 🛒 Корзина покупок
- 📝 Оформление заказов

# Создание виртуального окружения
python3 -m venv myshop_venv

# Активация окружения
source myshop_venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Применение миграций
python manage.py migrate

 # Создание суперпользователя
 python manage.py createsuperuser

 # Запуск сервера
 python manage.py runserver