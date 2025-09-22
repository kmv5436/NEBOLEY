from django.urls import path
from django.utils.translation import gettext_lazy as _
from . import views

app_name = 'shop'

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
]

