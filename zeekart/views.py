from django.http import HttpResponse
from django.shortcuts import render
from store.models import Product,Category
import random

def home(request):
    products=Product.objects.all()
    categories = Category.objects.all()
    products=list(products)
    random_prod=random.sample(products,k=3)
    print(f'all category aari hai kya ........  cccccccc',categories)
    context={
        'rand_prod':random_prod,
        'cat': categories,
    }
    return render(request,'store/home.html',context)

def store(request):
    return render(request,'store/store.html')