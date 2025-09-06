
from django.db import models
from store.models import Product,Variation
from accounts.models import Account
# Create your models here.

class Cart(models.Model):
    cart_id=models.CharField(max_length=50,null=True,blank=True)
    cart_added=models.DateField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.cart_id
    
    
    
class CartItem(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,null=True,blank=True)
    user=models.ForeignKey(Account,on_delete=models.CASCADE,null=True,blank=True)
    quantity=models.IntegerField(blank=True,null=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variation=models.ManyToManyField(Variation,blank=True)
    is_active=models.BooleanField(default=True)

    def subtotal(self):
        return self.product.price*self.quantity
    
   
    
    