from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import pytz


class Size(models.Model):
    """
    Модель размера товара
    """
    SIZE_CHOICES = [
        ('XS', _('Extra Small')),
        ('S', _('Small')),
        ('M', _('Medium')),
        ('L', _('Large')),
        ('XL', _('Extra Large')),
        ('XXL', _('Double Extra Large')),
        ('XXXL', _('Triple Extra Large')),
        ('UNI', _('Универсальный')),
        ('36', '36'),
        ('38', '38'),
        ('40', '40'),
        ('42', '42'),
        ('44', '44'),
        ('46', '46'),
        ('48', '48'),
        ('50', '50'),
        ('52', '52'),
        ('54', '54'),
    ]

    code = models.CharField(
        max_length=10,
        choices=SIZE_CHOICES,
        unique=True,
        verbose_name=_('Код размера'),
        help_text=_('Уникальный код размера')
    )
    name = models.CharField(
        max_length=50,
        verbose_name=_('Название размера'),
        help_text=_('Человекочитаемое название размера')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Описание размера'),
        help_text=_('Описание размера (необязательно)')
    )

    class Meta:
        verbose_name = _('Размер')
        verbose_name_plural = _('Размеры')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        """Автоматически заполняем name из выбранного code"""
        if not self.name:
            for code, name in self.SIZE_CHOICES:
                if code == self.code:
                    self.name = name
                    break
        super().save(*args, **kwargs)


class Category(models.Model):
    """
    Модель категории товаров
    """
    # ... остальные поля категории без изменений ...
    name = models.CharField(
        max_length=100,
        verbose_name=_('Название категории'),
        help_text=_('Введите название категории')
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name=_('URL-идентификатор'),
        help_text=_('Уникальный идентификатор для URL')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Описание категории'),
        help_text=_('Описание категории (необязательно)')
    )
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        verbose_name=_('Изображение категории'),
        help_text=_('Загрузите изображение категории (необязательно)')
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='children',
        verbose_name=_('Родительская категория'),
        help_text=_('Выберите родительскую категорию (если есть)')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активна'),
        help_text=_('Отметьте, если категория активна')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )

    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/catalog/{self.slug}/'


class Product(models.Model):
    """
    Модель товара
    """
    name = models.CharField(
        max_length=200,
        verbose_name=_('Название товара'),
        help_text=_('Введите название товара')
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name=_('URL-идентификатор'),
        help_text=_('Уникальный идентификатор для URL')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Описание товара'),
        help_text=_('Подробное описание товара (необязательно)')
    )
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name=_('Основное изображение'),
        help_text=_('Загрузите основное изображение товара (необязательно)')
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('Базовая цена (руб.)'),
        help_text=_('Введите базовую цену товара в рублях')
    )
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('Старая цена (руб.)'),
        help_text=_('Введите старую цену для акционных товаров (необязательно)')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('Категория'),
        help_text=_('Выберите категорию товара')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активен'),
        help_text=_('Отметьте, если товар активен')
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_('Рекомендуемый'),
        help_text=_('Отметьте, чтобы показать в рекомендуемых товарах')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )

    class Meta:
        verbose_name = _('Товар')
        verbose_name_plural = _('Товары')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
            models.Index(fields=['category']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/product/{self.slug}/'

    def is_on_sale(self):
        """Проверяет, есть ли у товара скидка"""
        return self.old_price is not None and self.old_price > self.price

    def get_discount_percentage(self):
        """Возвращает процент скидки, если товар со скидкой"""
        if self.is_on_sale():
            discount = ((self.old_price - self.price) / self.old_price) * 100
            return round(discount, 1)
        return 0

    def get_price_display(self):
        """Возвращает отформатированную цену в рублях"""
        return f'{self.price:.2f} ₽'

    def get_old_price_display(self):
        """Возвращает отформатированную старую цену в рублях"""
        if self.old_price:
            return f'{self.old_price:.2f} ₽'
        return None

    def get_available_sizes(self):
        """Возвращает доступные размеры с наличием"""
        return self.sizes.filter(productsize__in_stock=True)

    def has_multiple_sizes(self):
        """Проверяет, есть ли у товара несколько размеров"""
        return self.sizes.count() > 1


class ProductSize(models.Model):
    """
    Модель связи товара и размера с наличием и ценой
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_sizes',
        verbose_name=_('Товар')
    )
    size = models.ForeignKey(
        Size,
        on_delete=models.CASCADE,
        related_name='product_sizes',
        verbose_name=_('Размер')
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('Цена для размера (руб.)'),
        help_text=_('Цена для конкретного размера (если отличается от базовой)')
    )
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('Старая цена для размера (руб.)'),
        help_text=_('Старая цена для конкретного размера')
    )
    in_stock = models.BooleanField(
        default=True,
        verbose_name=_('В наличии'),
        help_text=_('Отметьте, если размер есть в наличии')
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Количество на складе'),
        help_text=_('Укажите количество товара данного размера на складе')
    )
    sku = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Артикул размера'),
        help_text=_('Уникальный артикул для комбинации товар-размер')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )

    class Meta:
        verbose_name = _('Размер товара')
        verbose_name_plural = _('Размеры товаров')
        unique_together = ['product', 'size']
        ordering = ['size__code']

    def __str__(self):
        return f"{self.product.name} - {self.size.code}"

    def get_final_price(self):
        """Возвращает конечную цену (цену размера или базовую цену товара)"""
        return self.price if self.price is not None else self.product.price

    def get_final_old_price(self):
        """Возвращает конечную старую цену"""
        return self.old_price if self.old_price is not None else self.product.old_price

    def get_price_display(self):
        """Возвращает отформатированную цену в рублях"""
        return f'{self.get_final_price():.2f} ₽'

    def get_old_price_display(self):
        """Возвращает отформатированную старую цену в рублях"""
        old_price = self.get_final_old_price()
        return f'{old_price:.2f} ₽' if old_price else None

    def is_on_sale(self):
        """Проверяет, есть ли скидка для этого размера"""
        old_price = self.get_final_old_price()
        return old_price is not None and old_price > self.get_final_price()


class ProductImage(models.Model):
    """
    Модель для дополнительных изображений товара
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Товар')
    )
    image = models.ImageField(
        upload_to='products/images/',
        verbose_name=_('Изображение')
    )
    alt_text = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Альтернативный текст'),
        help_text=_('Описание изображения для SEO')
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name=_('Основное изображение')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )

    class Meta:
        verbose_name = _('Изображение товара')
        verbose_name_plural = _('Изображения товаров')
        ordering = ['-is_main', 'created_at']

    def __str__(self):
        return _('Изображение для {}').format(self.product.name)


class ProductReview(models.Model):
    """
    Модель отзывов о товаре
    """
    RATING_CHOICES = [
        (1, _('1 - Ужасно')),
        (2, _('2 - Плохо')),
        (3, _('3 - Нормально')),
        (4, _('4 - Хорошо')),
        (5, _('5 - Отлично')),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Товар')
    )
    author_name = models.CharField(
        max_length=100,
        verbose_name=_('Имя автора')
    )
    email = models.EmailField(
        verbose_name=_('Email автора')
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        verbose_name=_('Рейтинг')
    )
    comment = models.TextField(
        verbose_name=_('Комментарий')
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name=_('Одобрен')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )

    class Meta:
        verbose_name = _('Отзыв')
        verbose_name_plural = _('Отзывы')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'is_approved']),
        ]

    def __str__(self):
        return _('Отзыв от {} для {}').format(self.author_name, self.product.name)
    
class Order(models.Model):
    """     Модель заказа    """
    STATUS_CHOICES = [
        ('new', _('Новый')),
        ('processing', _('В обработке')),
        ('shipped', _('Отправлен')),
        ('delivered', _('Доставлен')),
        ('cancelled', _('Отменен')),
    ]

    # Информация о клиенте
    customer_name = models.CharField(
        max_length=100,
        verbose_name=_('Имя клиента')
    )
    customer_email = models.EmailField(
        verbose_name=_('Email клиента')
    )
    customer_phone = models.CharField(
        max_length=20,
        verbose_name=_('Телефон клиента')
    )
    customer_address = models.TextField(
        verbose_name=_('Адрес доставки')
    )
    customer_comment = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Комментарий клиента')
    )

    # Информация о заказе
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Общая сумма')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name=_('Статус заказа')
    )
    order_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('Номер заказа')
    )

    # Даты
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )

    agreed_to_terms = models.BooleanField(
        verbose_name='Согласие с условиями',
        default=False
    )

    def created_at_moscow(self):
        """Возвращает время создания в московском времени в формате ЧЧ:ММ"""
        moscow_tz = pytz.timezone('Europe/Moscow')
        
        if timezone.is_naive(self.created_at):
            # Если время наивное, считаем что оно в UTC
            utc_time = timezone.make_aware(self.created_at, timezone=pytz.UTC)
            moscow_time = utc_time.astimezone(moscow_tz)
        else:
            # Время уже aware, конвертируем в Москву
            moscow_time = self.created_at.astimezone(moscow_tz)
            
        return moscow_time.strftime('%d.%m.%Y  %H:%M')
    
    created_at_moscow.short_description = 'Время (МСК)'
    created_at_moscow.admin_order_field = 'created_at'
    
    def created_at_full(self):
        """Полная дата и время в московском формате"""
        moscow_tz = pytz.timezone('Europe/Moscow')
        
        if timezone.is_naive(self.created_at):
            utc_time = timezone.make_aware(self.created_at, timezone=pytz.UTC)
            moscow_time = utc_time.astimezone(moscow_tz)
        else:
            moscow_time = self.created_at.astimezone(moscow_tz)
            
        return moscow_time.strftime('%d.%m.%Y %H:%M')
    
    created_at_full.short_description = 'Дата и время создания'


    class Meta:
        verbose_name = _('Заказ')
        verbose_name_plural = _('Заказы')
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.order_number} - {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Генерируем номер заказа
            import random
            import string
            from datetime import datetime
            
            date_part = datetime.now().strftime('%Y%m%d')
            random_part = ''.join(random.choices(string.digits, k=6))
            self.order_number = f"{date_part}{random_part}"
        
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """
    Модель товара в заказе
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Заказ')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_('Товар')
    )
    product_size = models.ForeignKey(
        ProductSize,
        on_delete=models.CASCADE,
        verbose_name=_('Размер товара')
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_('Количество')
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Цена за единицу')
    )

    class Meta:
        verbose_name = _('Товар в заказе')
        verbose_name_plural = _('Товары в заказе')

    def __str__(self):
        return f"{self.product.name} - {self.product_size.size.name}"

    @property
    def total_price(self):
        return self.price * self.quantity
    
    