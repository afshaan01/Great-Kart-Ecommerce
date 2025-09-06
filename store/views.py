from django.shortcuts import render
from .models import Product,Category,Variation
from django.core.paginator import Paginator
# Create your views here.

def search(request):
    
    search_input=request.GET.get('dhundo','')
    print(search_input)

    product_fetched=Product.objects.filter(product_name__icontains=search_input) if search_input else []
    product_count=product_fetched.count() if search_input else 0
        
    context={
            'product_fetched':product_fetched,
            'product_count':product_count,
            'search_input':search_input,
        }
    return render(request,'store/store.html',context)



def store(request,cat_slug=None):
    if cat_slug!=None:
        category=Category.objects.get(cat_slug=cat_slug)
        print(category)
        products=Product.objects.filter(category=category)
        print(f"filter products : ",products)
        
        paginator=Paginator(products,2)
    
        page=request.GET.get("page")
        paged_products=paginator.get_page(page)
        prod_count=products.count()
        print(prod_count)
        
        
    else:
        products=Product.objects.all()
        paginator=Paginator(products,2)
        page=request.GET.get("page")
        print(page)
        paged_products=paginator.get_page(page) 
        print(paged_products)
        products=paged_products.object_list
        print(products)
        prod_count=products.count()
        print(prod_count)
        
    if prod_count == 1:
        item_text = "item"
        
    else:
        item_text = "items"
    
    context={
        'all_prod':paged_products,
        'prod_count':prod_count,
        'item_text':item_text
    }
    return render(request,'store/store.html',context)


# def categories(request,cat_slug):
#     categories=Category.objects.filter(cat_slug=cat_slug)
#     print(categories)


def product_detail(request,cat_slug,product_slug):
    single_prod=Product.objects.get(category__cat_slug=cat_slug,product_slug=product_slug)
    print(single_prod.product_name)
    
    variations=Variation.objects.filter(product=single_prod.id)
    print(variations)
    
    colors=[]
    sizes=[]
    
    for i in variations:
        if i.variation_category == 'color':
            colors.append(i.variation_value)
        elif i.variation_category == 'size':
            sizes.append(i.variation_value)
    
    context={
        'single_product':single_prod,
        'colors':colors,
        'sizes':sizes,
        
    }
    return render(request,'store/product_detail.html',context)