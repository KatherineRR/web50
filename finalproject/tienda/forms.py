from django import forms
from tienda.models import Cart

class ProductForm(forms.ModelForm):

    class Meta:
        model = Cart
        fields = ('__all__')