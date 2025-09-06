from django.urls import path
from .import views

urlpatterns=[
    
    path('cart/',views.cart,name='cart'),
    path('add_cart/<int:product_id>/',views.add_cart,name='add_cart'),
    # path('checkout/',views.checkout,name='checkout'),
    path('cart_inc_dec/<int:product_id>/<int:cart_item_id>/',views.cart_inc_dec,name='cart_inc_dec'),
    path('cart_inc/<int:product_id>/<int:cart_item_id>/',views.cart_inc,name='cart_inc'),
    path('cart_item_remove/<int:product_id>/<int:cart_item_id>/',views.cart_item_remove,name='cart_item_remove'),
    
]