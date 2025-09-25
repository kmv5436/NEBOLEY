def cart_context(request):
    """Контекстный процессор для корзины"""
    cart = request.session.get('cart', {})
    return {
        'cart_count': len(cart.get('items', [])),
        'cart_total': cart.get('total', '0.00')
    }