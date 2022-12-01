from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, Cart, Order, Category, Type, Brand
from django.contrib import messages

from django.views.generic import View
from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse, HttpResponseRedirect

import stripe
from decimal import Decimal
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def index(request):
    cerrajeria = Product.objects.filter(tipo=1).order_by('pk')[:9]
    griferia = Product.objects.filter(tipo=2).order_by('pk')[:9]
    pinturas = Product.objects.filter(tipo=3).order_by('pk')[:9]

    context = {
        "cerrajeria": cerrajeria,
        "griferia": griferia,
        "pinturas": pinturas 
    }
    return render(request, 'tienda/index.html', context)


def products_list(request, tipo):
    product_list = Product.objects.filter(tipo=tipo)
    page = request.GET.get('page', 1)

    count = product_list.count()

    paginator = Paginator(product_list, 12)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        "products": products,
        "categories": Category.objects.filter(tipo=tipo),
        "brands": Brand.objects.filter(tipo=tipo),
        "tipo": Type.objects.get(pk=tipo), 
        "count": count
    }

    return render(request, 'tienda/product.html', context)


def product_category(request, categoria, tipo):
    product_list = Product.objects.filter(categoria=categoria)
    page = request.GET.get('page', 1)

    count = product_list.count()

    paginator = Paginator(product_list, 12)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        "products": products,
        "categories": Category.objects.filter(tipo=tipo),
        "brands": Brand.objects.filter(tipo=tipo),
        "tipo": Type.objects.get(pk=tipo),
        "count": count
    }

    return render(request, 'tienda/product.html', context)

def product_brand(request, marca, tipo):
    product_list = Product.objects.filter(marca=marca)
    page = request.GET.get('page', 1)

    count = product_list.count()

    paginator = Paginator(product_list, 12)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        "products": products,
        "categories": Category.objects.filter(tipo=tipo),
        "brands": Brand.objects.filter(tipo=tipo),
        "tipo": Type.objects.get(pk=tipo),
        "count": count
    }

    return render(request, 'tienda/product.html', context)

def product_detail(request, id):
    product = Product.objects.get(pk=id)
    product_list = Product.objects.filter(marca=product.marca)

    context = {
        "product": product,
        "products_related": product_list
    }

    return render(request, 'tienda/product-detail.html', context)


def about(request): 
    return render(request, 'tienda/about.html')

def contact(request):
    return render(request, 'tienda/contact.html')

@login_required(login_url='/login/')
def cart(request):
    total = 0
    try:
        products = Cart.objects.filter(user=request.user, pagado=0)
        for product in products:
            total = total + (product.producto.precio * product.cantidad) 
    except Cart.DoesNotExist:    
        messages.success(request, f'Error' )   

    context = {
        "key": settings.STRIPE_PUBLISHABLE_KEY,
        "products": products,
        "total": total
    }

    return render(request, 'tienda/cart.html', context)

@login_required(login_url='/login/')
def addcart(request, id):  
    if request.method == 'POST':
        try:
            product = Product.objects.get(pk=request.POST.get('producto'))
            if product.stock >= int(request.POST.get('cantidad')):
                try:
                    p = Cart.objects.get(user=request.user, pagado=0, producto=product.id) 
                    p.cantidad = p.cantidad + int(request.POST.get('cantidad'))
                    p.save()

                    product.stock = product.stock - int(request.POST.get('cantidad'))
                    product.save()
                    messages.success(request, p.producto.nombre ) 
                    return redirect('product_detail', id = product.id)
                except Cart.DoesNotExist:    
                    newproduct = Cart(producto=product, user=request.user, cantidad = request.POST.get('cantidad'))
                    newproduct.save()

                    product.stock = product.stock - int(request.POST.get('cantidad'))
                    product.save()
                    messages.success(request, newproduct.producto.nombre ) 
                    return redirect('product_detail', id = product.id) 
            else:
                messages.error(request, p.producto.nombre ) 
                return redirect('product_detail', id = product.id) 

        except Product.DoesNotExist:  
            messages.error(request, p.producto.nombre )   
            return redirect('product_detail', id = id)
        
    else:
        return redirect('product_detail', id = id, add = 0)

    return redirect('product_detail', id = product.id, add = 0)

@login_required(login_url='/login/')
def updatecart(request):
    if request.method == 'POST':
        try:
            product = Cart.objects.get(pk=request.POST.get('id'))

            if product.cantidad > int(request.POST.get('cantidad')):
                n = product.cantidad - int(request.POST.get('cantidad'))
                p = Product.objects.get(pk=product.producto.id)
                p.stock = p.stock + n
                p.save()

                product.cantidad = request.POST.get('cantidad')
                product.save()

            elif product.cantidad < int(request.POST.get('cantidad')):
                n = int(request.POST.get('cantidad')) - product.cantidad
                p = Product.objects.get(pk=product.producto.id)
                p.stock = p.stock - n
                p.save()

                product.cantidad = request.POST.get('cantidad')
                product.save()

        except Cart.DoesNotExist:    
            messages.success(request, f'!' )   

    return redirect('cart')

@login_required(login_url='/login/')
def deletecart(request, id):  
    try:
        product = Cart.objects.get(pk=id)
        
        p = Product.objects.get(pk=product.producto.id)
        p.stock = p.stock + product.cantidad
        p.save()

        product.delete()
    except Cart.DoesNotExist:
        messages.success(request, f'!' )

    return redirect('cart')

@login_required(login_url='/login/')
def checkout(request):
    total = 0
    try:
        products = Cart.objects.filter(user=request.user, pagado=0)
        neworder = Order(user=request.user, total = total)
        neworder.save()
        for product in products:
            product.pagado = 1
            product.save()
            total = total + (product.producto.precio * product.cantidad)
            neworder.productos.add(product)

        neworder.total = total
        neworder.save()

        charge = stripe.Charge.create(
            amount= int(total)*100,
            currency='usd',
            description="San Miguel hardware store",
            source=request.POST['stripeToken']
        )

        messages.success(request, f'Gracias por su compra!' )
    except Cart.DoesNotExist:    
        messages.error(request, f'Error su compra no se realizo')   

    return redirect('cart')

def sendemail(request):
     if request.method == 'POST':
        subject = request.POST.get('name')
        message = request.POST.get('message', 'phone-number')
        from_email = request.POST.get('email')

        if subject and message and from_email:
            try:
                send_mail(subject, message, from_email, ['asesorialegalhoy@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('contact')
        else:
            # In reality we'd use a form class
            # to get proper validation errors.
            return HttpResponse('Make sure all fields are entered and valid.')