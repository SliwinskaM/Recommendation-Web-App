from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'idx',
            'name',
            'shop_name',
            ]


class RawProductForm(forms.Form):
    idx = forms.IntegerField()
    name = forms.CharField()
    shop_name = forms.CharField()