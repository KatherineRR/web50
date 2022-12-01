from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Type(models.Model):
    nombre = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.nombre}"

class Category(models.Model):
    nombre = models.CharField(max_length=50)
    tipo = models.ForeignKey(Type, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.nombre}"

class Brand(models.Model):
    nombre = models.CharField(max_length=50)
    tipo = models.ForeignKey(Type, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.nombre}"

class Product(models.Model):
    nombre = models.CharField(max_length=50)
    marca = models.ForeignKey(Brand, on_delete=models.CASCADE)
    tipo = models.ForeignKey(Type, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Category, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=300)
    imagen = models.CharField(max_length=50)
    stock = models.IntegerField(default=1)
    precio = models.DecimalField(help_text="Precio en ₡", max_digits=7, decimal_places=2) 

    def __str__(self):
            return f"{self.marca} - {self.tipo} - {self.nombre} - ₡ {self.precio}"

class Cart(models.Model):
    CHOICES = (
        ('0', 'No'),
        ('1', 'Si'),
    ) 

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    pagado = models.CharField(max_length=5, choices=CHOICES, default=0)

    def __str__(self):
            return f"{self.user} - {self.producto} - Cantidad: {self.cantidad}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Cart, blank = False)
    total = models.DecimalField(help_text="Precio en ₡", max_digits=7, decimal_places=2) 
    fecha_de_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
            return f"{self.user} - ₡ {self.total}"

