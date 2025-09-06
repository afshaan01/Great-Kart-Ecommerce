from django.urls import path
from .import views

urlpatterns=[
       path('store/',views.store,name='store'),
       path('search/',views.search,name="search"),
       path('store/category/<str:cat_slug>/',views.store,name='store'),
       path('store/product_detail/<str:cat_slug>/<str:product_slug>/',views.product_detail,name="product_detail")
       
       # path('store/')
       # path('store/category/<str:cat_slug>/',views.categories,name="categories"),
       # path('category/<str:cat_slug>',views.categories,name="categories")
]