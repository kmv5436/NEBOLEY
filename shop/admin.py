from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db import models
from .models import Category, Product, ProductImage, ProductReview, Size, ProductSize
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_size', 'quantity', 'price']
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Используем кастомное поле для отображения времени
    list_display = ['order_number', 'customer_name', 'total_amount', 'status', 'created_at_moscow']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_email']
    readonly_fields = ['order_number', 'created_at_moscow', 'created_at_full', 'updated_at']
    inlines = [OrderItemInline]
    list_editable = ['status']
    
    fieldsets = (
        ('Информация о заказе', {
            'fields': ('order_number', 'total_amount', 'status')
        }),
        ('Информация о клиенте', {
            'fields': ('customer_name', 'customer_email', 'customer_phone', 'customer_address', 'customer_comment')
        }),
        ('Даты', {
            'fields': ('created_at_full', 'created_at_moscow', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Добавляем сортировку по времени создания
    ordering = ['-created_at']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'product_size', 'quantity', 'price']
    list_filter = ['order__status']
    search_fields = ['order__order_number', 'product__name']


class ProductSizeInline(admin.TabularInline):
    """
    Встроенная админка для размеров товара
    """
    model = ProductSize
    extra = 1
    verbose_name = _('Размер товара')
    verbose_name_plural = _('Размеры товара')
    
    fields = ['size', 'price', 'old_price', 'in_stock', 'stock_quantity', 'sku']


class ProductImageInline(admin.TabularInline):
    """
    Встроенная админка для изображений товара
    """
    model = ProductImage
    extra = 1
    verbose_name = _('Изображение товара')
    verbose_name_plural = _('Изображения товаров')
    
    fields = ['image', 'alt_text', 'is_main']


class ProductReviewInline(admin.TabularInline):
    """
    Встроенная админка для отзывов о товаре
    """
    model = ProductReview
    extra = 0
    verbose_name = _('Отзыв')
    verbose_name_plural = _('Отзывы')
    
    fields = ['author_name', 'email', 'rating', 'comment', 'is_approved', 'created_at']
    readonly_fields = ['author_name', 'email', 'rating', 'comment', 'created_at']
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    """
    Админка для размеров
    """
    list_display = ['code', 'name', 'description']
    list_filter = ['code']
    search_fields = ['code', 'name', 'description']
    ordering = ['code']


@admin.register(Product)  # ← ТОЛЬКО ОДНА РЕГИСТРАЦИЯ Product
class ProductAdmin(admin.ModelAdmin):
    """
    Админка для товаров
    """
    list_display = [
        'name', 'category', 'price_display', 'old_price_display', 
        'is_active', 'is_featured', 'created_at', 'sizes_count', 'total_stock'
    ]

    list_filter = [
        'category', 'is_active', 'is_featured', 'created_at', 'updated_at'
    ]
    ordering = ['-updated_at']  # Или добавить в существующий ordering
    search_fields = ['name', 'description', 'category__name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'is_featured']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ProductSizeInline, ProductImageInline, ProductReviewInline]
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        (_('Базовые цены'), {
            'fields': ('price', 'old_price'),
            'description': _('Эти цены будут использоваться, если не указаны цены для конкретных размеров')
        }),
        (_('Изображение'), {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        (_('Статус'), {
            'fields': ('is_active', 'is_featured')
        }),
        (_('Метаданные'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        from django.utils import timezone
        if change:
            obj.updated_at = timezone.now()
        super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        from django.utils import timezone
        if formset.model != Product:  # Если это inline'ы (размеры, изображения, отзывы)
            obj = form.instance
            if obj and obj.pk:
                obj.updated_at = timezone.now()
                obj.save(update_fields=['updated_at'])
        super().save_formset(request, form, formset, change)

    def price_display(self, obj):
        return obj.get_price_display()
    price_display.short_description = _('Базовая цена')
    
    def old_price_display(self, obj):
        return obj.get_old_price_display() or '-'
    old_price_display.short_description = _('Базовая старая цена')
    
    def sizes_count(self, obj):
        return obj.product_sizes.count()
    sizes_count.short_description = _('Кол-во размеров')
    
    def total_stock(self, obj):
        """Общее количество товара на складе"""
        total = obj.product_sizes.aggregate(total=models.Sum('stock_quantity'))['total']
        return total or 0
    total_stock.short_description = _('Общий запас')


@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    """
    Админка для размеров товаров
    """
    list_display = ['product', 'size', 'price_display', 'old_price_display', 'in_stock', 'stock_quantity', 'sku']
    list_filter = ['size', 'in_stock', 'product__category']
    search_fields = ['product__name', 'size__code', 'sku']
    list_editable = ['in_stock', 'stock_quantity', 'sku']
    readonly_fields = ['created_at', 'updated_at']
    
    def price_display(self, obj):
        return obj.get_price_display()
    price_display.short_description = _('Цена')
    
    def old_price_display(self, obj):
        return obj.get_old_price_display() or '-'
    old_price_display.short_description = _('Старая цена')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Админка для категорий
    """
    list_display = ['name', 'slug', 'parent', 'is_active', 'products_count', 'created_at']
    list_filter = ['is_active', 'created_at', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('name', 'slug', 'parent', 'description')
        }),
        (_('Изображение'), {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        (_('Статус'), {
            'fields': ('is_active',)
        }),
        (_('Метаданные'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = _('Количество товаров')
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('products')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """
    Админка для изображений товаров
    """
    list_display = ['product', 'image_preview', 'alt_text', 'is_main', 'created_at']
    list_filter = ['is_main', 'created_at']
    list_editable = ['is_main', 'alt_text']
    search_fields = ['product__name', 'alt_text']
    readonly_fields = ['created_at', 'image_preview']
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('product', 'image', 'alt_text', 'is_main')
        }),
        (_('Предпросмотр'), {
            'fields': ('image_preview',),
            'classes': ('collapse',)
        }),
        (_('Метаданные'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 100px; max-width: 100px;" />'
        return _('Нет изображения')
    image_preview.short_description = _('Предпросмотр')
    image_preview.allow_tags = True


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """
    Админка для отзывов о товарах
    """
    list_display = ['product', 'author_name', 'rating_stars', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    list_editable = ['is_approved']
    search_fields = ['author_name', 'product__name', 'comment']
    readonly_fields = ['created_at', 'rating_stars']
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('product', 'author_name', 'email')
        }),
        (_('Отзыв'), {
            'fields': ('rating', 'rating_stars', 'comment')
        }),
        (_('Статус'), {
            'fields': ('is_approved',)
        }),
        (_('Метаданные'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return f'{stars} ({obj.rating}/5)'
    rating_stars.short_description = _('Рейтинг')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')


# УБЕДИТЕСЬ, ЧТО НЕТ ДУБЛИРУЮЩИХ РЕГИСТРАЦИЙ:
# НЕТ: admin.site.register(Product, ProductAdmin)
# НЕТ: admin.site.register(Product)

