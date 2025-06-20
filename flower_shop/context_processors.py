from .cart import Cart

def cart(request):
    """
    Context processor to add the cart to the context.
    This allows access to the cart in all templates.
    """
    return {'cart': Cart(request)}