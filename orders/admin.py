from django.contrib import admin

# Register your models here.
from .models import Order,OrderProduct,Payment,Receipt

admin.site.register(Order)


admin.site.register(OrderProduct)

admin.site.register(Payment)

admin.site.register(Receipt)    