

# Create your views here.
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from orders.models import Order,OrderProduct
from .forms import UserProfileCoreForm
from accounts.models import UserProfile
from django.contrib import messages
# Create your views here.
@login_required(login_url="login")
def dashboard(request):
    return render(request,'dashboard/dashboard.html')

@login_required(login_url="login")
def my_orders(request):
    orders=Order.objects.filter(user=request.user)
    # op=OrderProduct.objects.filter(user=request.user,order=orders)
    # print(op)
    print(f'mere sare order dikha:{orders}')
    context={
        'orders':orders,
        # 'op':op,
    }
    return render(request,'dashboard/my_orders.html',context)


def order_detail(request,id):
    order=Order.objects.get(id=id)
    order_detail=OrderProduct.objects.filter(order=order)
    print(order_detail)
    list1=[]

    for i in order_detail:
        product_names=i.product.product_name
        variations=i.variation.all()
        product_image = i.product.image.url  
        product_price = i.product.price

        variation_list =  [str(variation) for variation in variations]

        list1.append({'product_names':product_names,
                      'product_price': product_price,
                      'variation_list':variation_list,
                      'product_image': product_image,})
    print(f'testing:{list1}')
    context={
        'order_prod':list1,
    }
    return render(request,'dashboard/detail.html',context)


def user_profile(request):
    profile,created=UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form=UserProfileCoreForm(request.POST, request.FILES)
        if form.is_valid():
            for field in form.cleaned_data:
                setattr(profile,field,form.cleaned_data[field])
            if 'profile_picture' in request.FILES:
                profile.profile_picyure=request.FILES['profile_picture']
            profile.save()
            messages.success(request,"Profile Updated SuccessFully")
            return redirect('user')
            
        else:
            messages.error(request,"Please Fix the Error Below")

    else:
        form=UserProfileCoreForm(initial={
            'address_line_1':profile.address_line_1,
            'address_line_2':profile.address_line_2,
            'city':profile.city,
            'state':profile.state,
            'country':profile.country,
            'pin_code':profile.pin_code,
            'phone_number':profile.phone_number

        })

    context={
        'profile':profile,
        'form':form,
    }

    return render(request,"dashboard/user.html",context)