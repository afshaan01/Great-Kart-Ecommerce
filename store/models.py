from django.db import models
from django.urls import reverse

class Category(models.Model):
    cat_name=models.CharField(max_length=50)
    cat_desc=models.CharField(max_length=255)
    cat_image=models.ImageField(upload_to='category/images')
    cat_slug=models.SlugField(max_length=50,null=True,blank=True)
    
    def __str__(self):
        return self.cat_name
    
    def get_url(self):
        return reverse('store',args=[self.cat_slug])
    
    class Meta:
        verbose_name="Category"
        verbose_name_plural="Categories"

class Product(models.Model):
    product_name=models.CharField(max_length=255)
    product_slug=models.SlugField(max_length=50,null=True,blank=True)
    price=models.FloatField()
    stock=models.IntegerField()
    desc=models.TextField(max_length=255)
    image=models.ImageField(upload_to='product/images')
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    date_time=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.product_name
    
variation_category_choice=(
    ('color','color'),
    ('size','size')
)
class Variation(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_category=models.CharField(max_length=100,choices=variation_category_choice)
    variation_value=models.CharField(max_length=100)
    is_active=models.BooleanField(default=True)
    created_date=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.variation_value