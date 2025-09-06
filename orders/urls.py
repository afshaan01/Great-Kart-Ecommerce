from django.urls import path
from .import views

urlpatterns=[
    path('checkout/',views.checkout,name="checkout"),
    path('payment_handler/',views.payment_handler,name="payment_handler"),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('receipt/<str:order_number>/', views.download_receipt, name='download_receipt'),
]
