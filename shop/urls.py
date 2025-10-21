from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import Sitemap
from .models import Product, Category
from . import views
from django.views.generic.base import TemplateView

app_name = 'shop'

class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'  # ← Указываем протокол

    def items(self):
        return Product.objects.filter(is_active=True)
    
    def location(self, obj):
        return f'/product/{obj.slug}/'  # Относительный путь

    def lastmod(self, obj):
        return obj.updated_at

class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6
    protocol = 'https'  # ← Указываем протокол

    def items(self):
        return Category.objects.filter(is_active=True)
    
    def location(self, obj):
        return f'/category/{obj.slug}/'
    
class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    protocol = 'https'

    def items(self):
        return ['product_list', 'category_list', 'about', 'contacts', 'delivery_info']

    def location(self, item):
        return reverse(f'shop:{item}')    

sitemaps = {
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'static': StaticViewSitemap,
}


urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/', views.category_list, name='category_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search_results, name='search_results'),
    path('featured/', views.featured_products, name='featured_products'),
    path('new/', views.new_arrivals, name='new_arrivals'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/update/<int:item_index>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_index>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('delivery/', views.delivery_info, name='delivery_info'),
    path('returns/', views.return_info, name='return_info'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('agreement/', views.user_agreement, name='user_agreement'),
    path('faq/', views.faq, name='faq'),
    path('contacts/', views.contacts, name='contacts'),
    path('about/', views.about, name='about'),
    path('payment/', views.payment_info, name='payment_info'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(
        template_name='robots.txt', 
        content_type='text/plain'
    )),
]

