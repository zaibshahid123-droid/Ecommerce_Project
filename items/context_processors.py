from .views import cart_item_count as _cart_item_count


def cart(request):
    """Makes {{ cart_count }} available in every template (nav badge)."""
    return {'cart_count': _cart_item_count(request)}
