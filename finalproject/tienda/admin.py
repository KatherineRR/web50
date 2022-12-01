from django.contrib import admin
from .models import Product, Cart, Order, Category, Type, Brand

# Register your models here.

admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Category)
admin.site.register(Type)
admin.site.register(Brand)