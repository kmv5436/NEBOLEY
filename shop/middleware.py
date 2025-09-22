class CartMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Копируем корзину из сессии в sessionStorage для JavaScript
        response = self.get_response(request)
        
        if hasattr(request, 'session') and 'cart' in request.session:
            cart = request.session['cart']
            if response.has_header('Content-Type') and 'text/html' in response['Content-Type']:
                content = response.content.decode('utf-8')
                if '</body>' in content:
                    script = f"""
                    <script>
                    sessionStorage.setItem('django_cart', JSON.stringify({cart}));
                    </script>
                    """
                    response.content = content.replace('</body>', script + '</body>')
        
        return response