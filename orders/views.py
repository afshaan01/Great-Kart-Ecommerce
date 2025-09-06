from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import random
from datetime import datetime
from cart.models import Cart, CartItem
from cart.views import _cart_id
from .models import Order,OrderProduct,Payment
from django.conf import settings
import razorpay
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import textwrap
from orders.models import Receipt
from django.shortcuts import get_object_or_404


client=razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required(login_url="login")
def checkout(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)

    total = 0
    tax = 0
    final_total = 0

    for item in cart_items:
        total += item.product.price * item.quantity
    
    if total > 0:
        tax = (total * 18) / 100
        final_total = total + tax

    if request.method == "POST":
       
        current_date =datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        random_num = random.randint(1000, 9999)
        order_number = f"{current_date}{random_num}"

       
        fname = request.POST.get('first-name', '')
        lname = request.POST.get('last-name', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        add1 = request.POST.get('address1', '')
        add2 = request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        country = request.POST.get('country', '')
        order_note = request.POST.get('order-note', '')
        postal_code = request.POST.get('postal-code', '')

        order = Order(
            user=user,
            order_number=order_number,
            first_name=fname,
            last_name=lname,
            phone=phone,
            email=email,
            address_line_1=add1,
            address_line_2=add2,
            city=city,
            state=state,
            country=country,
            postal_code=postal_code,
            order_note=order_note,
            total=final_total, 
            tax=tax
        )
        order.save()

       
        for item in cart_items:
            variations = item.variation.all()
            op = OrderProduct(
                user=request.user,
                order=order,
                product=item.product,
                quantity=item.quantity,
                product_price=item.product.price
            )
            op.save()
            op.variation.set(variations)
        
       
        cart_items.delete()

     
        razorpay_amount = int(final_total * 100) 
        razorpay_order = client.order.create({
            'amount': razorpay_amount,
            'currency': 'INR',
            'receipt': order_number,
            'payment_capture': '1' 
        })

        context = {
            'order': order,
            'cart_items': OrderProduct.objects.filter(user=request.user, order=order),
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'razorpay_amount': razorpay_amount,
            'razorpay_order_id': razorpay_order['id'],
            'currency': 'INR'
        }
        return render(request, 'orders/orderdetails.html', context)

    context = {
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'final_total': final_total
    }
    return render(request, 'orders/checkout.html', context)













from django.template.loader import render_to_string
from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import textwrap
from datetime import datetime

import logging
logger = logging.getLogger(__name__)


def generate_receipt(order, order_products):
    """Generate a PDF receipt for the order"""

    receipt_number = f"RCPT-{order.order_number}"
  
    buffer = BytesIO()
    

    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
  
    p.setFont("Helvetica-Bold", 14)
    
  
    p.drawString(1 * inch, height - 1 * inch, "Your Store Name")
    p.setFont("Helvetica", 10)
    p.drawString(1 * inch, height - 1.25 * inch, "123 Store Street, City, Country")
    p.drawString(1 * inch, height - 1.5 * inch, "Phone: +123456789 | Email: store@example.com")
    
 
    p.setFont("Helvetica-Bold", 16)
    p.drawString(1 * inch, height - 2 * inch, "PAYMENT RECEIPT")
    p.setFont("Helvetica", 10)
    p.drawString(1 * inch, height - 2.25 * inch, f"Receipt Number: {receipt_number}")
    p.drawString(1 * inch, height - 2.5 * inch, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    

    p.setFont("Helvetica-Bold", 12)
    p.drawString(1 * inch, height - 3 * inch, "Order Details:")
    p.setFont("Helvetica", 10)
    p.drawString(1 * inch, height - 3.25 * inch, f"Order Number: {order.order_number}")
    p.drawString(1 * inch, height - 3.5 * inch, f"Customer: {order.first_name} {order.last_name}")
    p.drawString(1 * inch, height - 3.75 * inch, f"Email: {order.email}")
    p.drawString(1 * inch, height - 4 * inch, f"Phone: {order.phone}")
    
   
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1 * inch, height - 4.5 * inch, "Billing Address:")
    p.setFont("Helvetica", 10)
    address_lines = [
        order.address_line_1,
        order.address_line_2 if order.address_line_2 else "",
        f"{order.city}, {order.state}",
        f"{order.country} - {order.postal_code}"
    ]
    for i, line in enumerate(address_lines):
        if line.strip():
            p.drawString(1 * inch, height - (4.75 + i*0.25) * inch, line)
    
    p.setFont("Helvetica-Bold", 10)
    p.drawString(1 * inch, height - 6 * inch, "Item")
    p.drawString(4 * inch, height - 6 * inch, "Quantity")
    p.drawString(5 * inch, height - 6 * inch, "Price")
    p.drawString(6.5 * inch, height - 6 * inch, "Total")
    p.line(1 * inch, height - 6.1 * inch, 7.5 * inch, height - 6.1 * inch)
    

    y_position = height - 6.5 * inch
    for item in order_products:
        p.setFont("Helvetica", 9)
      
        product_text = f"{item.product.product_name}"
        if item.variation.all().exists():
            variations = ", ".join([f"{v.variation_category}: {v.variation_value}" for v in item.variation.all()])
            product_text += f" ({variations})"
        
  
        for line in textwrap.wrap(product_text, width=40):
            p.drawString(1 * inch, y_position, line)
            y_position -= 0.2 * inch
        
        p.drawString(4 * inch, y_position + 0.2 * inch, str(item.quantity))
        p.drawString(5 * inch, y_position + 0.2 * inch, f"₹{item.product_price:.2f}")
        p.drawString(6.5 * inch, y_position + 0.2 * inch, f"₹{item.product_price * item.quantity:.2f}")
        y_position -= 0.4 * inch
    
   
    p.setFont("Helvetica-Bold", 10)
    p.drawString(5 * inch, y_position - 0.5 * inch, "Subtotal:")
    p.drawString(6.5 * inch, y_position - 0.5 * inch, f"₹{order.total - order.tax:.2f}")
    
    p.drawString(5 * inch, y_position - 0.8 * inch, "Tax (18%):")
    p.drawString(6.5 * inch, y_position - 0.8 * inch, f"₹{order.tax:.2f}")
    
    p.drawString(5 * inch, y_position - 1.1 * inch, "Total:")
    p.drawString(6.5 * inch, y_position - 1.1 * inch, f"₹{order.total:.2f}")
    
    p.setFont("Helvetica-Bold", 10)
    p.drawString(1 * inch, y_position - 1.8 * inch, "Payment Information:")
    p.setFont("Helvetica", 9)
    p.drawString(1 * inch, y_position - 2.1 * inch, f"Method: {order.payment.payment_method}")
    p.drawString(1 * inch, y_position - 2.4 * inch, f"Transaction ID: {order.payment.payment_id}")
    p.drawString(1 * inch, y_position - 2.7 * inch, f"Status: {order.payment.status}")
    p.drawString(1 * inch, y_position - 3 * inch, f"Paid At: {order.payment.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
   
    p.setFont("Helvetica", 8)
    p.drawString(1 * inch, 0.5 * inch, "Thank you for shopping with us!")
    p.drawString(1 * inch, 0.3 * inch, "For any queries, please contact support@example.com")
    
    p.showPage()
    p.save()

    receipt = Receipt.objects.create(
        order=order,
        receipt_number=receipt_number
    )
    
   
    from django.core.files.base import ContentFile
    receipt.pdf_file.save(
        f'receipt_{receipt_number}.pdf',
        ContentFile(buffer.getvalue())
    )
    receipt.save()
    
    return receipt



from django.http import FileResponse


from django.http import FileResponse, Http404

def download_receipt(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
        receipt = Receipt.objects.get(order=order)
        
        if not receipt.pdf_file or not receipt.pdf_file.path:
            raise Http404("Receipt file not found")
        
        return FileResponse(open(receipt.pdf_file.path, 'rb'), as_attachment=True,
                            filename=f'receipt_{receipt.receipt_number}.pdf')
        
    except (Order.DoesNotExist, Receipt.DoesNotExist, FileNotFoundError):
        return redirect('order_history')

    
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import razorpay
from .models import Order, OrderProduct, Payment, Receipt
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import textwrap
from datetime import datetime

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@csrf_exempt
def payment_handler(request):
    if request.method == 'POST':
        try:
            payment_id = request.POST.get('razorpay_payment_id')
            razorpay_order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')
            
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

          
            client.utility.verify_payment_signature(params_dict)
  
            razorpay_order = client.order.fetch(razorpay_order_id)
            order_number = razorpay_order['receipt']
            
            order = Order.objects.get(order_number=order_number)
            order_products = OrderProduct.objects.filter(order=order)
            
          
            payment = Payment.objects.create(
                user=order.user,
                payment_id=payment_id,
                payment_method="Razorpay",
                amount_paid=order.total,
                status="Completed"
            )
            
          
            order.payment = payment
            order.is_ordered = True
            order.status = 'Completed'
            order.save()
            

            receipt = generate_receipt(order, order_products)
            
           
            request.session['receipt_context'] = {'order_id': order.id}
            
           
            return redirect('payment_success')
        
        except Order.DoesNotExist:
            return render(request, 'payment/failure.html', {'error': 'Order not found'})
        except Exception as e:
            return render(request, 'payment/failure.html', {'error': str(e)})
    
    return redirect('payment_success')

def payment_success(request):
    context = {}
    receipt_context = request.session.pop('receipt_context', None)
    if receipt_context:
        order = get_object_or_404(Order, id=receipt_context['order_id'])
        order_products = OrderProduct.objects.filter(order=order)
      
        receipt = get_object_or_404(Receipt, order=order)
        context = {
            'order': order,
            'receipt': receipt,
        }
    else:
        context = {'error': 'No order found. Please check your order history.'}
    return render(request, 'payment/success.html', context)

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders
    }
    return render(request, 'orders/order_history.html', context)














# --------------------------------------------------------------------------------------------------------------------------------------


# purana wala comment hai



# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# import random
# import datetime
# from cart.models import Cart,CartItem
# from cart.views import _cart_id
# from .models import Order
# # Create your views here.
# @login_required(login_url="login")
# def checkout(request):

#     user=request.user
#     random_num=random.randint(1,1000)
#     current_date=datetime.date()
#     order_number=str(current_date)+(str(random_num))
#     print(order_number)
#     try:
#         if request.user.is_authenticated:
#             cart_items = CartItem.objects.filter(user=request.user)
#         else:
#             cart = Cart.objects.get(cart_id=_cart_id(request))  # Fetch cart ID
#             print(f"Cart ID: {cart}")
#             print(type(cart))
#             cart_items = CartItem.objects.filter(cart=cart)
#             print(f'Cart Items: {cart_items}')

#         total = 0
#         tax = 0
#         final_total = 0

#         for item in cart_items:
#             total += item.product.price * item.quantity

#         if total > 0:
#             tax = (total * 18) / 100
#             final_total = total + tax

#         context = {
#             'cart_items': cart_items,
#             'total': total,
#             'tax': tax,
#             'final_total': final_total
#         }
#     except Exception:
#         pass




#     if request.method == "POST":
#         fname=request.POST['first-name']
#         lname=request.POST['last-name']
#         phone=request.POST['phone']
#         email=request.POST['email']
#         add1=request.POST['address1']
#         add2=request.POST['address2']
#         city=request.POST['city']
#         state=request.POST['state']
#         country=request.POST['country']
#         order_note=request.POST['order-note']
#         postal_code=request.POST['postal-code']
#         order=Order(user=request.user,order_number=order_number,first_name=fname,last_name=lname,phone=phone,
#               email=email,address_line_1=add1,address_line_2=add2,city=city,state=state,country=country,
#               order_note=order_note,postal_code=postal_code,total=total,tax=tax)
#         order.save()

#     return render(request,'orders/checkout.html',context)





# purana wala comment hai

# --------------------------------------------------------------------------------------------------------------------------------------

    
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# import random
# from datetime import datetime
# from cart.models import Cart, CartItem
# from cart.views import _cart_id
# from .models import Order,OrderProduct,Payment
# from django.conf import settings
# import razorpay
# from django.views.decorators.csrf import csrf_exempt
# from io import BytesIO
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter
# from reportlab.lib.units import inch
# import textwrap
# from orders.models import Receipt
# from django.shortcuts import get_object_or_404

# --------------------------------------------------------------------------------------------------------------------------------------




# purana wala comment hai





# client=razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# import random
# import datetime
# from cart.models import Cart, CartItem
# from cart.views import _cart_id
# from .models import Order, OrderProduct, Payment
# from django.conf import settings
# import razorpay
# from django.views.decorators.csrf import csrf_exempt
# from django.template.loader import render_to_string
# from django.http import HttpResponse
# from io import BytesIO
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter
# from reportlab.lib.units import inch
# import textwrap



# purana wala comment hai



# --------------------------------------------------------------------------------------------------------------------------------------


# client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# @login_required(login_url="login")
# def checkout(request):
#     user = request.user
#     cart_items = CartItem.objects.filter(user=user)

#     total = 0
#     tax = 0
#     final_total = 0

#     for item in cart_items:
#         total += item.product.price * item.quantity
    
#     if total > 0:
#         tax = (total * 18) / 100
#         final_total = total + tax

#     if request.method == "POST":
 
#         current_date =datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         random_num = random.randint(1000, 9999)
#         order_number = f"{current_date}{random_num}"


#         fname = request.POST.get('first-name', '')
#         lname = request.POST.get('last-name', '')
#         phone = request.POST.get('phone', '')
#         email = request.POST.get('email', '')
#         add1 = request.POST.get('address1', '')
#         add2 = request.POST.get('address2', '')
#         city = request.POST.get('city', '')
#         state = request.POST.get('state', '')
#         country = request.POST.get('country', '')
#         order_note = request.POST.get('order-note', '')
#         postal_code = request.POST.get('postal-code', '')

    
#         order = Order(
#             user=user,
#             order_number=order_number,
#             first_name=fname,
#             last_name=lname,
#             phone=phone,
#             email=email,
#             address_line_1=add1,
#             address_line_2=add2,
#             city=city,
#             state=state,
#             country=country,
#             postal_code=postal_code,
#             order_note=order_note,
#             total=final_total, 
#             tax=tax
#         )
#         order.save()

      
#         for item in cart_items:
#             variations = item.variation.all()
#             op = OrderProduct(
#                 user=request.user,
#                 order=order,
#                 product=item.product,
#                 quantity=item.quantity,
#                 product_price=item.product.price
#             )
#             op.save()
#             op.variation.set(variations)
        
  
#         cart_items.delete()

#         razorpay_amount = int(final_total * 100)  
#         razorpay_order = client.order.create({
#             'amount': razorpay_amount,
#             'currency': 'INR',
#             'receipt': order_number,
#             'payment_capture': '1' 
#         })

#         context = {
#             'order': order,
#             'cart_items': OrderProduct.objects.filter(user=request.user, order=order),
#             'razorpay_key_id': settings.RAZORPAY_KEY_ID,
#             'razorpay_amount': razorpay_amount,
#             'razorpay_order_id': razorpay_order['id'],
#             'currency': 'INR'
#         }
#         return render(request, 'orders/orderdetails.html', context)

#     context = {
#         'cart_items': cart_items,
#         'total': total,
#         'tax': tax,
#         'final_total': final_total
#     }
#     return render(request, 'orders/checkout.html', context)

# --------------------------------------------------------------------------------------------------------------------------------------


# purana wala comment pehle ka




# @login_required(login_url="login")
# def checkout(request):
#     # current_date = datetime.date.today().strftime('%Y%m%d')  # Format: YYYYMMDD
#     # random_num = random.randint(1000, 9999)
#     # order_number = f"{current_date}{random_num}"
#     # op=OrderProduct()
#     # op.order=order_number
#     # op.user=request.user

#     user = request.user
#     cart_items = CartItem.objects.filter(user=user)#here all cartitems added by user is fetched

#     total = 0
#     tax = 0
#     final_total = 0

#     for item in cart_items:#here iam looping to each cartitem in cartitems
#         total=total+item.product.price * item.quantity#total
       
    
#     if total > 0:
#         tax = (total * 18) / 100#here we are applying 18 percent tax
#         final_total = total + tax
#     print(f'checkout wala final total:{final_total}')

#     # client=razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))
#     # DATA={
#     #     'amount':final_total,
#     #     'currency':'INR',
#     #     "receipt":f"order_rcpt_id_{user.id}"
#     #     }
#     # razorpay_order=client.order.create(data=DATA)

#     if request.method == "POST":
#         # Generate unique order number
#         current_date = datetime.date.today().strftime('%Y%m%d')  # Format: YYYYMMDD
#         random_num = random.randint(1000, 9999)
#         order_number = f"{current_date}{random_num}"

#         # Get form data
#         fname = request.POST.get('first-name', '')
#         lname = request.POST.get('last-name', '')
#         phone = request.POST.get('phone', '')
#         email = request.POST.get('email', '')
#         add1 = request.POST.get('address1', '')
#         add2 = request.POST.get('address2', '')
#         city = request.POST.get('city', '')
#         state = request.POST.get('state', '')
#         country = request.POST.get('country', '')
#         order_note = request.POST.get('order-note', '')
#         postal_code = request.POST.get('postal-code', '')

#         # Save Order
#         order = Order(
#             user=user,
#             order_number=order_number,
#             first_name=fname,
#             last_name=lname,
#             phone=phone,
#             email=email,
#             address_line_1=add1,
#             address_line_2=add2,
#             city=city,
#             state=state,
#             country=country,
#             postal_code=postal_code,
#             order_note=order_note,
#             total=total,
#             tax=tax
#         )
    
#         order.save()
#         for item in cart_items:
#             variations=item.variation.all()
#             op=OrderProduct(user=request.user,order=order,product=item.product,quantity=item.quantity,product_price=item.product.price)
#             op.save()
#             op.variation.set(variations)
#             op.save()
#         cart_items.delete()
       
#         order_details=Order.objects.get(user=request.user,order_number=order.order_number,first_name=order.first_name,last_name=order.last_name,
#                           phone=order.phone,email=order.email,address_line_1=order.address_line_1,
#                           address_line_2=order.address_line_2,city=order.city,state=order.state,
#                           country=order.country,postal_code=order.postal_code,order_note=order.order_note,
#                           total=order.total,tax=order.tax)
#         print(f'aa rha hai kya ek checkout ka data:{order_details.address_line_1}')

#         order_prod_fetched=OrderProduct.objects.filter(user=request.user,order=order)
#         context={
#             'order':order_details,
#             'cart_items':order_prod_fetched,
#         }
#         return render(request,'orders/orderdetails.html',context)


#         # Optional: Redirect to ordr summary / confirmation page
#         # return redirect('order_summary', order_number=order_number)

#     context = {
#         'cart_items': cart_items,
#         'total': total,
#         'tax': tax,
#         'final_total': final_total
#     }

#     return render(request, 'orders/checkout.html', context)

# @csrf_exempt
# def payment_handler(request):
#     if request.method =='POST':
#         try:
#             data=request.POST

#             client=razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))
#             params_dict={
#                 'razorpay_order_id':data['razorpay_order_id'],
#                 'razorpay_payment_id':data['razorpay_payment_id'],
#                 'razorpay_signature':data['razorpay_signature'],
#             }
#             client.utility.verify_payment_signature(params_dict)
#             order=Order.objects.get(order_number=params_dict['razorpay_order_id'])
#             payment=Payment.objects.create(user=order.user,payment_id=params_dict['razorpay_payment_id'],
#                                    payment_method="razorpay",
#                                    amount_paid=order.total,
#                                    status="Success")
#             order.payment = payment
#             order.is_ordered = True
#             order.status = 'Processing'
#             order.save()
#             return render(request, 'payment/success.html', {'order': order})
        
#         except Exception as e:
#             print("Payment failed:", str(e))
#             return render(request, 'payment/failure.html')
            
#     return redirect('/')

# @csrf_exempt
# def payment_handler(request):
#     if request.method == 'POST':
#         try:
#             payment_id = request.POST.get('razorpay_payment_id')
#             razorpay_order_id = request.POST.get('razorpay_order_id')
#             signature = request.POST.get('razorpay_signature')
            
#             params_dict = {
#                 'razorpay_order_id': razorpay_order_id,
#                 'razorpay_payment_id': payment_id,
#                 'razorpay_signature': signature
#             }

#             # Verify payment signature
#             client.utility.verify_payment_signature(params_dict)
            
#             # Get order by Razorpay order ID (note: this is different from your order_number)
#             # You might need to store the Razorpay order ID in your Order model
#             # For now, we'll use the receipt number which should match your order_number
#             razorpay_order = client.order.fetch(razorpay_order_id)
#             order_number = razorpay_order['receipt']
            
#             order = Order.objects.get(order_number=order_number)
#             order_products = OrderProduct.objects.filter(order=order)
            
#             # Save payment details
#             payment = Payment.objects.create(
#                 user=order.user,
#                 payment_id=payment_id,
#                 payment_method="Razorpay",
#                 amount_paid=order.total,
#                 status="Completed"
#             )
            
#             # Update order status
#             order.payment = payment
#             order.is_ordered = True
#             order.status = 'Completed'
#             order.save()
#             request.session['receipt_context'] = {
#            'order_id': order.id
#             }
#             return redirect('payment_success')  # use a named URL pattern

         


            
         
        
#         # except Order.DoesNotExist:
#         #     return render(request, 'payment/failure.html', {'error': 'Order not found'})
#         except Exception as e:
#             return render(request, 'payment/failure.html', {'error': str(e)})
    
#     return redirect('/')



# purana wala comment 


# --------------------------------------------------------------------------------------------------------------------------------------



# from django.template.loader import render_to_string
# from django.http import HttpResponse
# from io import BytesIO
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter
# from reportlab.lib.units import inch
# import textwrap
# from datetime import datetime

# @csrf_exempt
# def payment_handler(request):
#     if request.method == 'POST':
#         try:
#             payment_id = request.POST.get('razorpay_payment_id')
#             razorpay_order_id = request.POST.get('razorpay_order_id')
#             signature = request.POST.get('razorpay_signature')
            
#             params_dict = {
#                 'razorpay_order_id': razorpay_order_id,
#                 'razorpay_payment_id': payment_id,
#                 'razorpay_signature': signature
#             }

#             client.utility.verify_payment_signature(params_dict)
            
         
#             razorpay_order = client.order.fetch(razorpay_order_id)
#             order_number = razorpay_order['receipt']
            
#             order = Order.objects.get(order_number=order_number)
#             order_products = OrderProduct.objects.filter(order=order)
            
           
#             payment = Payment.objects.create(
#                 user=order.user,
#                 payment_id=payment_id,
#                 payment_method="Razorpay",
#                 amount_paid=order.total,
#                 status="Completed"
#             )
            
           
#             order.payment = payment
#             order.is_ordered = True
#             order.status = 'Completed'  
#             order.save()
            
     
#             receipt = generate_receipt(order, order_products)
            
           

#             context={
#                 'order':order,
#                 'receipt':receipt,
#             }
            
#             return render(request, 'payment/success.html',context)
        
        

#         except Exception as e:
#             return render(request, 'payment/failure.html', {'error': str(e)})
    
        
#     return redirect('success')

# def generate_receipt(order, order_products):
#     """Generate a PDF receipt for the order"""
 
#     receipt_number = f"RCPT-{order.order_number}"
    

#     buffer = BytesIO()
    

#     p = canvas.Canvas(buffer, pagesize=letter)
#     width, height = letter
    

#     p.setFont("Helvetica-Bold", 14)

#     p.drawString(1 * inch, height - 1 * inch, "Your Store Name")
#     p.setFont("Helvetica", 10)
#     p.drawString(1 * inch, height - 1.25 * inch, "123 Store Street, City, Country")
#     p.drawString(1 * inch, height - 1.5 * inch, "Phone: +123456789 | Email: store@example.com")
    
  
#     p.setFont("Helvetica-Bold", 16)
#     p.drawString(1 * inch, height - 2 * inch, "PAYMENT RECEIPT")
#     p.setFont("Helvetica", 10)
#     p.drawString(1 * inch, height - 2.25 * inch, f"Receipt Number: {receipt_number}")
#     p.drawString(1 * inch, height - 2.5 * inch, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
  
#     p.setFont("Helvetica-Bold", 12)
#     p.drawString(1 * inch, height - 3 * inch, "Order Details:")
#     p.setFont("Helvetica", 10)
#     p.drawString(1 * inch, height - 3.25 * inch, f"Order Number: {order.order_number}")
#     p.drawString(1 * inch, height - 3.5 * inch, f"Customer: {order.first_name} {order.last_name}")
#     p.drawString(1 * inch, height - 3.75 * inch, f"Email: {order.email}")
#     p.drawString(1 * inch, height - 4 * inch, f"Phone: {order.phone}")
    

#     p.setFont("Helvetica-Bold", 12)
#     p.drawString(1 * inch, height - 4.5 * inch, "Billing Address:")
#     p.setFont("Helvetica", 10)
#     address_lines = [
#         order.address_line_1,
#         order.address_line_2 if order.address_line_2 else "",
#         f"{order.city}, {order.state}",
#         f"{order.country} - {order.postal_code}"
#     ]
#     for i, line in enumerate(address_lines):
#         if line.strip():
#             p.drawString(1 * inch, height - (4.75 + i*0.25) * inch, line)
    

#     p.setFont("Helvetica-Bold", 10)
#     p.drawString(1 * inch, height - 6 * inch, "Item")
#     p.drawString(4 * inch, height - 6 * inch, "Quantity")
#     p.drawString(5 * inch, height - 6 * inch, "Price")
#     p.drawString(6.5 * inch, height - 6 * inch, "Total")
#     p.line(1 * inch, height - 6.1 * inch, 7.5 * inch, height - 6.1 * inch)
    

#     y_position = height - 6.5 * inch
#     for item in order_products:
#         p.setFont("Helvetica", 9)
      
#         product_text = f"{item.product.product_name}"
#         if item.variation.all().exists():
#             variations = ", ".join([f"{v.variation_category}: {v.variation_value}" for v in item.variation.all()])
#             product_text += f" ({variations})"
        

#         for line in textwrap.wrap(product_text, width=40):
#             p.drawString(1 * inch, y_position, line)
#             y_position -= 0.2 * inch
        
#         p.drawString(4 * inch, y_position + 0.2 * inch, str(item.quantity))
#         p.drawString(5 * inch, y_position + 0.2 * inch, f"₹{item.product_price:.2f}")
#         p.drawString(6.5 * inch, y_position + 0.2 * inch, f"₹{item.product_price * item.quantity:.2f}")
#         y_position -= 0.4 * inch
    
   
#     p.setFont("Helvetica-Bold", 10)
#     p.drawString(5 * inch, y_position - 0.5 * inch, "Subtotal:")
#     p.drawString(6.5 * inch, y_position - 0.5 * inch, f"₹{order.total - order.tax:.2f}")
    
#     p.drawString(5 * inch, y_position - 0.8 * inch, "Tax (18%):")
#     p.drawString(6.5 * inch, y_position - 0.8 * inch, f"₹{order.tax:.2f}")
    
#     p.drawString(5 * inch, y_position - 1.1 * inch, "Total:")
#     p.drawString(6.5 * inch, y_position - 1.1 * inch, f"₹{order.total:.2f}")
    

#     p.setFont("Helvetica-Bold", 10)
#     p.drawString(1 * inch, y_position - 1.8 * inch, "Payment Information:")
#     p.setFont("Helvetica", 9)
#     p.drawString(1 * inch, y_position - 2.1 * inch, f"Method: {order.payment.payment_method}")
#     p.drawString(1 * inch, y_position - 2.4 * inch, f"Transaction ID: {order.payment.payment_id}")
#     p.drawString(1 * inch, y_position - 2.7 * inch, f"Status: {order.payment.status}")
#     p.drawString(1 * inch, y_position - 3 * inch, f"Paid At: {order.payment.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
 
#     p.setFont("Helvetica", 8)
#     p.drawString(1 * inch, 0.5 * inch, "Thank you for shopping with us!")
#     p.drawString(1 * inch, 0.3 * inch, "For any queries, please contact support@example.com")
    
    
#     p.showPage()
#     p.save()
    
  
#     receipt = Receipt.objects.create(
#         order=order,
#         receipt_number=receipt_number
#     )
    

#     from django.core.files.base import ContentFile
#     receipt.pdf_file.save(
#         f'receipt_{receipt_number}.pdf',
#         ContentFile(buffer.getvalue())
#     )
#     receipt.save()
    
#     return receipt



# from django.http import FileResponse



# --------------------------------------------------------------------------------------------------------------------------------------

# purana wala comment hai




# def download_receipt(request, order_number):
#     try:
#         order = Order.objects.get(order_number=order_number, user=request.user)
#         receipt = Receipt.objects.get(order=order)
#         response = FileResponse(receipt.pdf_file, as_attachment=True, filename=f'receipt_{receipt.receipt_number}.pdf')
#         return response
#     except (Order.DoesNotExist, Receipt.DoesNotExist):
#         return redirect('order_history')  # or show an error           


# purana wala comment hai

# --------------------------------------------------------------------------------------------------------------------------------------



# from django.http import FileResponse, Http404

# def download_receipt(request, order_number):
#     try:
#         order = Order.objects.get(order_number=order_number, user=request.user)
#         receipt = Receipt.objects.get(order=order)
        
#         if not receipt.pdf_file or not receipt.pdf_file.path:
#             raise Http404("Receipt file not found")
        
#         return FileResponse(open(receipt.pdf_file.path, 'rb'), as_attachment=True,
#                             filename=f'receipt_{receipt.receipt_number}.pdf')
        
#     except (Order.DoesNotExist, Receipt.DoesNotExist, FileNotFoundError):
#         return redirect('order_history')

    

# def payment_success(request):
#     context = {}
#     receipt_context = request.session.pop('receipt_context', None)
#     if receipt_context:
#         order = get_object_or_404(Order, id=receipt_context['order_id'])
#         order_products = OrderProduct.objects.filter(order=order)
#         receipt = generate_receipt(order, order_products)

#         context = {
#             'order': order,
#             'receipt': receipt,
#         }
#     return render(request, 'payment/success.html', context)



















































# from django.shortcuts import render,redirect
# from django.contrib.auth.decorators import login_required
# from .models import Order,OrderProduct,Payment
# import random
# from datetime import date
# import datetime
# from cart.models import Cart,CartItem
# from cart.views import _cart_id
# import razorpay
# from django.conf import settings
# from django.views.decorators.csrf import csrf_exempt
# Create your views here.

# client=razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))

# @login_required(login_url="login")
# def checkout(request):
   
#     user=request.user
#     random_num=random.randint(1000,9999)
#     current_date=date.today().strftime('%Y%m%d')
#     order_number=str(current_date)+(str(random_num))
#     print(f"...000 order number aaya kya ???....",order_number)


#     if request.user.is_authenticated:
#          cart_items = CartItem.objects.filter(user=user)
#     else:

        # try:
            # cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
            # if not cart:
                # Optional: create a new cart or redirect user
                # return redirect('home')  # ya koi error message dikhana

    #         cart_items = CartItem.objects.filter(cart=cart)
    #         print(f"dekho wo aagaya ", cart_items)

    # total = 0
    # for item in cart_items:
    #     total += item.product.price * item.quantity
        
    # tax = (total * 18) / 100
    # final_total = total + tax
    # except Exception:
#     cart_count=0
#     context = {
#         'cart_items': cart_items,
#         'total': total,
#         'tax': tax,
#         'final_total': final_total
#     }

  
#     client=razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))
#     DATA={
#          'amount':int(final_total * 100),
#          'currency':'INR',
#          'receipt':f"order_receipt_id_{user.id}"
#     }
#     razorpay_order=client.order.create(data=DATA)

#     if request.method == 'POST':
#         firstname=request.POST['first_name']
#         lastname=request.POST['last_name']
#         phone=request.POST['phone']
#         email=request.POST['email']
#         add1=request.POST['address1']
#         add2=request.POST['address2']
#         city=request.POST['city']
#         state=request.POST['state']
#         country=request.POST['country']
#         postal_code=request.POST['postal_code']
#         order_note=request.POST['order_note']

#         order=Order(user=user,first_name=firstname,last_name=lastname,email=email,phone=phone,address_line_1=add1,address_line_2=add2,city=city,state=state,country=country,postal_code=postal_code,order_note=order_note,total=total,tax=tax,order_number=order_number)
#         order.save()

#         for item in cart_items:
#            variations=item.variation.all()
#            op=OrderProduct(user=request.user,order=order,product=item.product,quantity=item.quantity,product_price=item.product.price)
#            op.save()

#            op.variation.set(variations)
#            op.save()

#         cart_items.delete()



#         order_details=Order.objects.get(user=request.user,order_number=order.order_number,first_name=order.first_name,last_name=order.last_name,
#                           phone=order.phone,email=order.email,address_line_1=order.address_line_1,address_line_2=order.address_line_2,
#                           city=order.city,state=order.state,country=order.country,postal_code=order.postal_code,order_note=order.order_note,
#                           total=order.total,tax=order.tax)
#         print(f"order aaya kya bantaye",order.first_name)

#         order_product_fetch=OrderProduct.objects.filter(user=request.user,order=order)

#         context={
#             'order':order_details,
#             'cart_items':order_product_fetch,
#             'total': total,
#             'tax': tax,
#             'final_total': final_total,
#             'razorpay_key_id': settings.RAZORPAY_KEY_ID,
#             'razorpay_order_id': razorpay_order['id'],
#             'razorpay_amount': int(final_total * 100), 
#         }
#         return render(request,'orders/orderdetails.html',context)

#     return render(request,"orders/checkout.html")
  

# @csrf_exempt
# def payment_handler(request):
#      if request.method == 'POST':
#           try:
#                payment_id = request.POST.get('razorpay_payment_id')
#                razorpay_order_id = request.POST.get('razorly_order_id')
#                signature = request.POST.get('razorpay_signature')
               
#                params_dict={
#                     'razorpay_order_id':razorpay_order_id,
#                     'razorpay_payment_id':payment_id,
#                     'razorpay_signature':signature,
#                }
#                client.utility.verify_payments_signature(params_dict)

#                razorpay_order= client.order.fetch(razorpay_order_id)
#                order_number= razorpay_order['receipt']
#                order=Order.objects.get(order_number=order_number)

#                payment=Payment.objects.create(user=order.user,payment_id=payment_id,
#                                               payment_method='Razorpay',
#                                               amount_paid=order.total,
#                                               status="Completed")

#                order.payment = payment
#                order.is_ordered = True
#                order.status = 'Processing'
#                order.save()

#                return render(request,'payment/success.html',{'order':order})
#           except Exception as e :
#                print("Payment failed",str(e))
#                return render(request,"payment/failure.html")
          
#      return redirect('/')
               

            
  