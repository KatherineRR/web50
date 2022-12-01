from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('products_list/<int:tipo>', views.products_list, name='products_list'),
    path('product_category/<int:categoria>/<int:tipo>', views.product_category, name='product_category'),
    path('product_brand/<int:marca>/<int:tipo>', views.product_brand, name='product_brand'),
    path('product_detail/<int:id>', views.product_detail, name='product_detail'),

    path('cart', views.cart, name='cart'),
    path('addcart/<int:id>', views.addcart, name = 'addcart'),
    path('deletecart/<int:id>', views.deletecart, name = 'deletecart'),
    path('updatecart', views.updatecart, name = 'updatecart'),
    path('checkout', views.checkout, name = 'checkout'),

    path('about', views.about, name='about'),

    path('contact', views.contact, name='contact'),    
    path('sendemail', views.sendemail, name='sendemail'), 
]