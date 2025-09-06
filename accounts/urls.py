from django.urls import path
from . import views

urlpatterns=[
    path('register/',views.register,name="register"),
    path('loginUser/',views.loginUser,name="login"),
    path('logoutUser/',views.logoutUser,name="logout"),
    path('activate/<uidb64>/<token>/',views.activate,name="activate"),
    path('forgotpassword/',views.forgotpassword,name="fp"),
    path('resetpasswordvalidate/<uidb64>/<token>/',views.resetpassword_validate,name="resetpassword_validate"),
    path('resetpassconfirm',views.resetpassconfirm,name="resetpassconfirm"),
    
]