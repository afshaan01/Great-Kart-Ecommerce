from django.urls import path


from . import views
urlpatterns = [

    path('dashboard/',views.dashboard,name="dashboard"),
    path('order_history/',views.my_orders,name="my_orders"),
    path('orders/<int:id>',views.order_detail, name="order_detail"),
    path('user_profile/',views.user_profile,name="user"),





]