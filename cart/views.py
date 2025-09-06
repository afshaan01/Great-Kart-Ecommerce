from django.shortcuts import render,redirect
from store.models import Product,Variation
from django.db.models import Q
from .models import Cart,CartItem
# Create your views here.

def _cart_id(request):
    cart=request.session.session_key
    if not cart:
        request.session.create()
        cart = request.session.session_key 

    return cart
    
def add_cart(request,product_id):
    product=Product.objects.get(id=product_id)
    print(f"yaha mere products aayege",product)
    if request.user.is_authenticated:
        if request.method=='POST':
            colors=request.POST.get('colors')
            sizes=request.POST.get('sizes')
            print(f"variation check kar raha hoon aaye ya nahi.............",colors,sizes)

            color_variation = Variation.objects.filter(product=product,variation_category__iexact='color',variation_value__iexact=colors).first()
            size_variation = Variation.objects.filter(product=product,variation_category__iexact='size',variation_value__iexact=sizes).first()

            variations=[]
            if color_variation:
                variations.append(color_variation)
            if size_variation:
                variations.append(size_variation)

            if not variations:
                print("no matching variations found")
                return redirect('cart')
            
       

            cart_items= CartItem.objects.filter(user=request.user,product=product)
            
            existing_cart_item = None
            for item in cart_items:
                if set(item.variation.all()) == set(variations):
                    existing_cart_item = item
                    break

            if existing_cart_item:

                existing_cart_item.quantity += 1
                existing_cart_item.save()

            else:
                cart_item=CartItem.objects.create(
                user=request.user if request.user.is_authenticated else None,
                product=product,
                quantity=1
                )

                if variations:
                    cart_item.variation.set(variations)
                cart_item.save()

            return redirect('cart')
    else:
         if request.method=='POST':
            colors=request.POST.get('colors')
            sizes=request.POST.get('sizes')
            print(f"variation check kar raha hoon aaye ya nahi.............",colors,sizes)

            color_variation = Variation.objects.filter(product=product,variation_category__iexact='color',variation_value__iexact=colors).first()
            size_variation = Variation.objects.filter(product=product,variation_category__iexact='size',variation_value__iexact=sizes).first()

            variations=[]
            if color_variation:
                variations.append(color_variation)
            if size_variation:
                variations.append(size_variation)

            if not variations:
                print("no matching variations found")
                return redirect('cart')
            
            cart, created = Cart.objects.get_or_create(cart_id =_cart_id(request))

            cart_items= CartItem.objects.filter(cart=cart,product=product)
            
            existing_cart_item = None
            for item in cart_items:
                if set(item.variation.all()) == set(variations):
                    existing_cart_item = item
                    break

            if existing_cart_item:

                existing_cart_item.quantity += 1
                existing_cart_item.save()

            else:
                cart_item = CartItem.objects.create(cart=cart,product=product, quantity=1)

                if variations:
                    cart_item.variation.set(variations)
                cart_item.save()

            return redirect('cart')



        # cart_item, created = CartItem.objects.get_or_create(cart=cart,product=product)


      


        # if not created:
        #     cart_item.quantity += 1
        # cart_item.save()

        # cart_item.variation.set(variations)
        # cart_item.quantity = (cart_item.quantity or 0) + 1
        # cart_item.save()

        # if variations:
        #     cart_item.variation.set(variations)

        # return redirect('cart')

        # color_variation= Variation.objects.filter(product=product,variation_category__iexact='color',variation_value__iexact=colors).first()
        
        # size_variation= Variation.objects.filter(product=product,variation_category__iexact='size',variation_value__iexact=sizes).first()

        
        # Variation.objects.filter(product=product,variation_category=colors)
        
def cart(request):
    
    if request.user.is_authenticated:
         cart_items = CartItem.objects.filter(user=request.user)
    else:

        # try:
            cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
            if not cart:
                # Optional: create a new cart or redirect user
                return redirect('home')  # ya koi error message dikhana

            cart_items = CartItem.objects.filter(cart=cart)
            print(f"dekho wo aagaya ", cart_items)

    total = 0
    for item in cart_items:
        total += item.product.price * item.quantity
    tax = (total * 18) / 100
    final_total = total + tax
    # except Exception:
    cart_count=0
    context = {
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'final_total': final_total
    }

    return render(request, 'cart/cart.html', context)
    

# def cart(request):
#     cart=Cart.objects.get(cart_id=_cart_id(request))
#     cart_items=CartItem.objects.filter(cart=cart)
#     print(f"dekho wo aagaya ",cart_items)

#     total=0
#     for item in cart_items:
#         total=total+(item.product.price*item.quantity)
#         tax=(total*18)/100
#         final_total=total+tax

    
#     context={
#         'cart_items':cart_items,
#         'total':total,
#         'tax':tax,
#         'final_total':final_total
#     }

#     return render(request,'cart/cart.html',context)


# def checkout(request):
#     return render(request,'cart/checkout.html')


def cart_inc_dec(request,product_id,cart_item_id):
    if request.user.is_authenticated:
        cart_item=CartItem.objects.get(user=request.user,product=product_id)
        if cart_item.quantity<=1:
          cart_item.delete()
        else:
            cart_item.quantity-=1
            cart_item.save()
    else:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_item=CartItem.objects.get(product=product_id,id=cart_item_id,cart=cart)
        if cart_item.quantity<=1:
            cart_item.delete()
        else:
            cart_item.quantity-=1
            cart_item.save()
    return redirect('cart')


def cart_inc(request,product_id,cart_item_id):
    if request.user.is_authenticated:
        cart_item=CartItem.objects.get(user=request.user,product=product_id)
        cart_item.quantity+=1
        cart_item.save()
    else:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_item=CartItem.objects.get(cart=cart,product=product_id,id=cart_item_id)
        cart_item.quantity+=1
        cart_item.save()
    return redirect('cart')

def cart_item_remove(request,cart_item_id,product_id):
    if request.user.is_authenticated:
        cart_item=CartItem.objects.get(user=request.user,product=product_id)
        cart_item.delete()

    else:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_item=CartItem.objects.get(product=product_id,id=cart_item_id)
        cart_item.delete()
    return redirect('cart')