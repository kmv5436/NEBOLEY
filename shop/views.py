from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Exists, OuterRef, Sum
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from decimal import Decimal
from .models import Product, Category, ProductSize, Size

# ... остальные импорты и функции ...

def get_cart(request):
    """Получение корзины из сессии"""
    cart = request.session.get('cart', {})
    if 'items' not in cart:
        cart['items'] = []
    if 'total' not in cart:
        cart['total'] = Decimal('0.00')
    return cart

def save_cart(request, cart):
    """Сохранение корзины в сессии"""
    request.session['cart'] = cart
    request.session.modified = True

def update_cart_total(cart):
    """Обновление общей суммы корзины"""
    total = Decimal('0.00')
    for item in cart['items']:
        total += Decimal(item['price']) * item['quantity']
    cart['total'] = str(total)  # Сохраняем как строку для сессии

def add_to_cart(request):
    """
    Добавление товара в корзину
    """
    if request.method == 'POST':
        try:
            product_id = request.POST.get('product_id')
            size_id = request.POST.get('size_id')
            quantity = int(request.POST.get('quantity', 1))
            
            product = get_object_or_404(Product, id=product_id)
            product_size = get_object_or_404(ProductSize, id=size_id, product=product)
            
            # Проверяем наличие
            if not product_size.in_stock:
                messages.error(request, 'Этот размер временно отсутствует')
                return redirect('shop:product_detail', product_slug=product.slug)
            
            if quantity > product_size.stock_quantity:
                messages.error(request, 'Недостаточно товара на складе')
                return redirect('shop:product_detail', product_slug=product.slug)
            
            # Получаем корзину из сессии
            cart = get_cart(request)
            
            # Проверяем, есть ли уже такой товар в корзине
            item_index = None
            for i, item in enumerate(cart['items']):
                if item['product_id'] == product_id and item['size_id'] == size_id:
                    item_index = i
                    break
            
            final_price = product_size.get_final_price()
            
            if item_index is not None:
                # Обновляем количество существующего товара
                cart['items'][item_index]['quantity'] += quantity
            else:
                # Добавляем новый товар в корзину
                cart['items'].append({
                    'product_id': product_id,
                    'size_id': size_id,
                    'quantity': quantity,
                    'price': str(final_price),
                    'product_name': product.name,
                    'size_name': product_size.size.name,
                    'image_url': product.image.url if product.image else ''
                })
            
            # Обновляем общую сумму
            update_cart_total(cart)
            
            # Сохраняем корзину в сессии
            save_cart(request, cart)
            
            messages.success(request, f'Товар "{product.name}" ({product_size.size.name}) добавлен в корзину!')
            
        except (ValueError, ProductSize.DoesNotExist):
            messages.error(request, 'Ошибка при добавлении в корзину')
        
        return redirect('shop:product_detail', product_slug=product.slug)
    
    return redirect('shop:product_list')

def cart_view(request):
    """
    Представление для отображения корзины покупок
    """
    cart = get_cart(request)
    
    # Получаем полную информацию о товарах в корзине
    cart_items = []
    for item in cart['items']:
        try:
            product = Product.objects.get(id=item['product_id'])
            product_size = ProductSize.objects.get(id=item['size_id'], product=product)
            
            cart_items.append({
                'index': cart['items'].index(item),
                'product': product,
                'product_size': product_size,
                'quantity': item['quantity'],
                'total_price': Decimal(item['price']) * item['quantity'],
                'image_url': item.get('image_url', '')
            })
        except (Product.DoesNotExist, ProductSize.DoesNotExist):
            # Удаляем несуществующий товар из корзины
            cart['items'].remove(item)
    
    # Обновляем корзину после проверки
    update_cart_total(cart)
    save_cart(request, cart)
    
    context = {
        'page_title': 'Корзина покупок',
        'cart_items': cart_items,
        'cart_total': Decimal(cart['total']),
        'cart_count': len(cart['items'])
    }
    
    return render(request, 'shop/cart.html', context)

def update_cart(request, item_index):
    """
    Обновление количества товара в корзине
    """
    if request.method == 'POST':
        cart = get_cart(request)
        
        try:
            item_index = int(item_index)
            if 0 <= item_index < len(cart['items']):
                new_quantity = int(request.POST.get('quantity', 1))
                
                if new_quantity > 0:
                    # Проверяем наличие на складе
                    item = cart['items'][item_index]
                    product_size = ProductSize.objects.get(
                        id=item['size_id'], 
                        product_id=item['product_id']
                    )
                    
                    if new_quantity > product_size.stock_quantity:
                        messages.error(request, 'Недостаточно товара на складе')
                    else:
                        cart['items'][item_index]['quantity'] = new_quantity
                        update_cart_total(cart)
                        save_cart(request, cart)
                        messages.success(request, 'Количество товара обновлено')
                else:
                    # Удаляем товар если количество = 0
                    return remove_from_cart(request, item_index)
                    
        except (ValueError, IndexError, ProductSize.DoesNotExist):
            messages.error(request, 'Ошибка при обновлении корзины')
    
    return redirect('shop:cart')

def remove_from_cart(request, item_index):
    """
    Удаление товара из корзины
    """
    cart = get_cart(request)
    
    try:
        item_index = int(item_index)
        if 0 <= item_index < len(cart['items']):
            removed_item = cart['items'].pop(item_index)
            update_cart_total(cart)
            save_cart(request, cart)
            
            # Получаем информацию о товаре для сообщения
            try:
                product = Product.objects.get(id=removed_item['product_id'])
                product_size = ProductSize.objects.get(id=removed_item['size_id'])
                messages.success(request, f'Товар "{product.name}" ({product_size.size.name}) удален из корзины')
            except (Product.DoesNotExist, ProductSize.DoesNotExist):
                messages.success(request, 'Товар удален из корзины')
                
    except (ValueError, IndexError):
        messages.error(request, 'Ошибка при удалении товара')
    
    return redirect('shop:cart')

def clear_cart(request):
    """
    Очистка корзины
    """
    cart = get_cart(request)
    cart['items'] = []
    cart['total'] = '0.00'
    save_cart(request, cart)
    messages.success(request, 'Корзина очищена')
    return redirect('shop:cart')


def product_list(request, category_slug=None):
    """
    Представление для отображения списка всех товаров или товаров по категории
    """
    # Создаем подзапрос для проверки наличия товара
    in_stock_subquery = ProductSize.objects.filter(
        product=OuterRef('pk'),
        in_stock=True
    )
    
    # Получаем все активные товары, у которых есть хотя бы один размер в наличии
    products = Product.objects.filter(
        is_active=True
    ).annotate(
        has_stock=Exists(in_stock_subquery)
    ).filter(has_stock=True)
    
    # Если передан slug категории, фильтруем товары по категории
    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=category)
    
    # Получаем параметры фильтрации из GET-запроса
    size_filter = request.GET.get('size')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    search_query = request.GET.get('q')
    
    # Применяем фильтры
    if size_filter and size_filter != 'all':
        # Фильтруем товары, у которых есть указанный размер в наличии
        products = products.filter(
            product_sizes__size__code=size_filter,
            product_sizes__in_stock=True
        ).distinct()
    
    if price_min:
        try:
            # Фильтруем по базовой цене товара
            products = products.filter(price__gte=float(price_min))
        except (ValueError, TypeError):
            pass
    
    if price_max:
        try:
            # Фильтруем по базовой цене товара
            products = products.filter(price__lte=float(price_max))
        except (ValueError, TypeError):
            pass
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Сортировка
    sort_by = request.GET.get('sort', 'name')
    order = request.GET.get('order', 'asc')
    
    sort_fields = {
        'name': 'name',
        'price': 'price',
        'created': 'created_at',
        'popular': '?',
    }
    
    if sort_by in sort_fields:
        field = sort_fields[sort_by]
        if order == 'desc':
            field = f'-{field}'
        products = products.order_by(field)
    
    # Пагинация
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    # Получаем все активные категории для меню
    categories = Category.objects.filter(is_active=True)
    
    # Уникальные размеры для фильтра (только те, что есть в наличии)
    available_sizes = Size.objects.filter(
        product_sizes__in_stock=True
    ).distinct()
    
    # Тексты для сортировки
    sort_options = {
        'name': _('По названию'),
        'price': _('По цене'),
        'created': _('По дате добавления'),
        'popular': _('По популярности'),
    }
    
    order_options = {
        'asc': _('По возрастанию'),
        'desc': _('По убыванию'),
    }
    
    context = {
        'products': products_page,
        'category': category,
        'categories': categories,
        'available_sizes': available_sizes,
        'size_filter': size_filter,
        'price_min': price_min or '',
        'price_max': price_max or '',
        'search_query': search_query or '',
        'sort_by': sort_by,
        'order': order,
        'sort_options': sort_options,
        'order_options': order_options,
        'page_title': _('Каталог товаров') if not category else category.name,
    }
    
    return render(request, 'shop/product_list.html', context)


def product_detail(request, product_slug):
    """
    Представление для отображения детальной страницы товара
    """
    product = get_object_or_404(
        Product, 
        slug=product_slug, 
        is_active=True
    )
    
    # Получаем ВСЕ размеры товара (и в наличии, и нет)
    all_sizes = product.product_sizes.all().select_related('size').order_by('size__code')
    
    # Получаем изображения товара
    product_images = product.images.all()
    
    # Создаем подзапрос для проверки наличия связанных товаров
    in_stock_subquery = ProductSize.objects.filter(
        product=OuterRef('pk'),
        in_stock=True
    )
    
    # Получаем связанные товары (из той же категории) которые есть в наличии
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).annotate(
        has_stock=Exists(in_stock_subquery)
    ).filter(has_stock=True).exclude(id=product.id)[:4]
    
    # Получаем одобренные отзывы
    reviews = product.reviews.filter(is_approved=True)
    
    # Средний рейтинг
    from django.db.models import Avg
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'product': product,
        'all_sizes': all_sizes,  # Все размеры вместо только доступных
        'product_images': product_images,
        'related_products': related_products,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'page_title': product.name,
    }
    
    return render(request, 'shop/product_detail.html', context)

def category_list(request):
    """
    Представление для отображения списка всех категорий
    """
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'categories': categories,
        'page_title': _('Категории товаров'),
    }
    
    return render(request, 'shop/category_list.html', context)


def search_results(request):
    """
    Представление для отображения результатов поиска
    """
    # Создаем подзапрос для проверки наличия товара
    in_stock_subquery = ProductSize.objects.filter(
        product=OuterRef('pk'),
        in_stock=True
    )
    
    query = request.GET.get('q')
    products = Product.objects.filter(
        is_active=True
    ).annotate(
        has_stock=Exists(in_stock_subquery)
    ).filter(has_stock=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    # Пагинация
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    context = {
        'products': products_page,
        'search_query': query,
        'results_count': products.count(),
        'page_title': _('Результаты поиска'),
    }
    
    return render(request, 'shop/search_results.html', context)


def featured_products(request):
    """
    Представление для отображения рекомендуемых товаров
    """
    # Создаем подзапрос для проверки наличия товара
    in_stock_subquery = ProductSize.objects.filter(
        product=OuterRef('pk'),
        in_stock=True
    )
    
    products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).annotate(
        has_stock=Exists(in_stock_subquery)
    ).filter(has_stock=True)
    
    context = {
        'products': products,
        'title': _('Рекомендуемые товары'),
        'page_title': _('Рекомендуемые товары'),
    }
    
    return render(request, 'shop/featured_products.html', context)


def new_arrivals(request):
    """
    Представление для отображения новых поступлений
    """
    from datetime import datetime, timedelta
    
    # Создаем подзапрос для проверки наличия товара
    in_stock_subquery = ProductSize.objects.filter(
        product=OuterRef('pk'),
        in_stock=True
    )
    
    # Товары, добавленные за последние 30 дней
    thirty_days_ago = datetime.now() - timedelta(days=30)
    products = Product.objects.filter(
        is_active=True,
        created_at__gte=thirty_days_ago
    ).annotate(
        has_stock=Exists(in_stock_subquery)
    ).filter(has_stock=True).order_by('-created_at')
    
    context = {
        'products': products,
        'title': _('Новые поступления'),
        'page_title': _('Новые поступления'),
    }
    
    return render(request, 'shop/new_arrivals.html', context)

