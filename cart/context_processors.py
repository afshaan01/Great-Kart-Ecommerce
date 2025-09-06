from .views import _cart_id
from .models import Cart,CartItem

def counter(request):
    cart_count=0
    try:
        if request.user.is_authenticated:
            cart_item=CartItem.objects.filter(user=request.user)
            cart_count=0
            for item in cart_item:
              cart_count=cart_count+item.quantity
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart)
            cart_count=0
            for item in cart_items:
                cart_count=cart_count+item.quantity
    except Cart.DoesNotExist:
        cart_count=0
    except Cart.MultipleObjectsReturned:
        if request.user.is_authenticated:
            cart_item=CartItem.objects.filter(user=request.user).first()
            cart_count=0
            for item in cart_items:
                 cart_count=cart_count+item.quantity
            print(f" cart ids are ",carts)
        else:
            carts=Cart.objects.filter(cart_id=_cart_id(request)).first()
            cart_items=CartItem.objects.filter(cart=cart)
            cart_count=0
            for item in cart_items:
                    cart_count=cart_count+item.quantity
            print(f" cart ids are ",carts)
    return dict(count=cart_count)