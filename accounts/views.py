from django.shortcuts import render,redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages,auth
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.conf import settings 
from cart.models import Cart,CartItem
from cart.views import _cart_id
# Create your views here.

def register(request):
    if request.method == "POST":
      form=RegistrationForm(request.POST)
      if form.is_valid():
          first_name=form.cleaned_data['first_name']
          last_name=form.cleaned_data['last_name']
          phone_number=form.cleaned_data['phone_number']
          email=form.cleaned_data['email']
          password=form.cleaned_data['password']
          username=email.split('@')[0]
          user=Account.objects.create_user(first_name=first_name,last_name=last_name,
                                      email=email,password=password,username=username)
          user.phone_number=phone_number
          user.is_active=False
          user.save()
          messages.success(request," Your Form is Submitted ")
          
          current_site=get_current_site(request)
          print(current_site)
          mail_subject="please activate your account"
          message=render_to_string('accounts/account_verification_email.html',
          {
              'user':user,
              'domain':current_site.domain,
              'uid':urlsafe_base64_encode(force_bytes(user.pk)),
              'token':default_token_generator.make_token(user),
              
          })
          to_email=email
          email_message=EmailMessage(mail_subject,message,from_email=settings.EMAIL_HOST_USER,to=[to_email])
          email_message.send()
          messages.success(request,f"Thank you for regestring we have sent a activate email at {to_email}")
          return redirect("login")
                                      
          
    else:
        form=RegistrationForm()
        
    context={
        'form':form
    }
    return render(request,'accounts/register.html',context)

def loginUser(request):
    if request.method=='POST':
      email=request.POST['email']
      password=request.POST['pass']
      user=auth.authenticate(email=email,password=password)
      print(user)
      if user is not None:
        cart_count=0
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request)) #yaha cart_id match hori hai  session id wala hai yeh
            cart_items=CartItem.objects.filter(cart=cart)#jo cart id match hori hai us cart id ke cart_items fetch hore hai ye yeh without
            # login wala hai 
            
            user_cart_items = CartItem.objects.filter(user=user)

            guest_variations= {tuple(item.variation.all()) : item for item in cart_items}
            user_variations= {tuple(item.variation.all()) : item for item in user_cart_items}

            # cart_item_ex_var=[]
            # for item in cart_items:
            #     variations=item.variation.all()
            #     cart_item_ex_var.append(variations)     
            # print(f"..........aagaya dekho variation......",cart_item_ex_var) 

            # cart_item_new_var=[]

            for variation, guest_item in guest_variations.items():
                if variation in user_variations:
                    existing_item = user_variations[variation]
                    existing_item.quantity += guest_item.quantity
                    existing_item.save()
                    guest_item.delete()
                
                else:
                    guest_item.user = user
                    guest_item.cart = None
                    guest_item.save()

            cart.delete()



            # cart_items=CartItem.objects.filter(user=user)
            # for item in cart_items:
            #     variations=item.variation.all()
            #     cart_item_new_var.append(variations)     
            # print(f"..........aagaya dekho variation......",cart_item_new_var) 

            # for variation in cart_item_ex_var:
            #     if variation in cart_item_new_var:
            #         cart_item=CartItem.objects.filter(user=user, variation__in=variations).first()
            #         cart_item.quantity=1
            #         cart_item.save()
            #         cart_item.delete()

            #     else:
            #         for items in cart_items:
            #             if set(item.variation.all()) == set(variation):
            #                 cart_item.user=user
            #                 cart_item.cart=None
            #                 cart_item.save()


        
        except Cart.DoesNotExist:
            pass


        auth.login(request,user)
        messages.success(request,"you have successfully logged in")
        return redirect('home')
      else:
          messages.error(request,"login failed")
          return redirect('login')
    return render(request,'accounts/login.html')

@login_required(login_url="login")
def logoutUser(request): 
    auth.logout(request)
    messages.success(request,"you are successfully logged out")
    return redirect('login')

def activate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    
    except Exception:
        user=None
    if user is not None and default_token_generator.check_token(user,token):
            user.is_active=True
            user.save()
            messages.success(request,"you are activated")
            return redirect("login")
    else:
        messages.error(request,"invalid activation link")
        return redirect("register")
    
    
def forgotpassword(request):
    if request.method == 'POST':
        email=request.POST.get('email')
        user=Account._default_manager.get(email=email)
        print(f"yeh hai woh user",user)
        
        if user is not None:
            
          current_site=get_current_site(request)
        #   print(current_site)
          mail_subject="password reset email"
          message=render_to_string('accounts/password_reset_email.html',
          {
              'user':user,
              'domain':current_site,
              'uid':urlsafe_base64_encode(force_bytes(user.pk)),
              'token':default_token_generator.make_token(user),
              
          })
          to_email=email
          send_mail=EmailMessage(mail_subject,message,from_email=settings.EMAIL_HOST_USER,to=[to_email])
          send_mail.send()
          messages.success(request,f"we have sent a password reset email to {email}")
          return redirect("login")
            
    return render(request,'accounts/forgotpassword.html')


def resetpassword_validate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    
    except Exception:
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['reset_user_id']=user.id
        
        messages.success(request,"you are verified please reset your password")
        return redirect("resetpassconfirm")
    else:
        messages.error(request,"invalid activation link")
        return redirect("register")
    
    
Account=get_user_model()
def resetpassconfirm(request):
    if request.method == 'POST':
        new_password=request.POST.get('passwd')
        user_id=request.session.get('reset_user_id')
        if user_id:
            user=Account.objects.get(pk=user_id)
            user.password=make_password(new_password)
            user.save()
            messages.success(request,"password reset successfully")
            
            del request.session['reset_user_id']
            return redirect('login')
            
        else:
            messages.error(request," session expired. Please request a new reset link")
            return redirect('reset_password')
    return render(request,'accounts/confirm_password.html')