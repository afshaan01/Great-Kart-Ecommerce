from django.contrib import admin
from .models import Category,Product,Variation

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields={'cat_slug':('cat_name',)}
    list_display=['id','cat_name','cat_image','cat_desc']
admin.site.register(Category,CategoryAdmin)

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields={'product_slug':('product_name',)}
    list_display=['product_name','price','stock','desc','image']
admin.site.register(Product,ProductAdmin)


admin.site.register(Variation)